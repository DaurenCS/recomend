from fastapi import Depends,  Security,  Request, HTTPException
import app.models.models as mdl
from sqlalchemy.orm import Session, joinedload
from database.database import session
import pickle
import os
import faiss
from collections import defaultdict
import app.models.schemas as sch
import random
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
import jwt
from jose import JWTError, ExpiredSignatureError
from typing import List



import numpy as np

import redis

r = redis.Redis(
    host="redis-17009.c8.us-east-1-2.ec2.redns.redis-cloud.com",  
    port=17009,  
    password="zd66qejs39E8MbD1QLx3QlLwtH3F7BEB",  # Add password if required
    db=0,  
    decode_responses=True  
)

SECRET_KEY = "IP03O5Ekg91g5jw=="
ALGORITHM = "HS256"
security = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

embedding_dim = 128
faiss_index_file = "faiss.index"
if os.path.exists(faiss_index_file):
    faiss_index = faiss.read_index(faiss_index_file)
else:
    faiss_index = faiss.IndexFlatL2(embedding_dim)

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self):
        return self.db.query(mdl.User).all()
    
    def get_user(self, id: int):
        return self.db.query(mdl.User).filter(mdl.User.id == id).first()
    
class EmbeddingRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_embedding(self, user_id: int):
        return self.db.query(mdl.ProfileVector).filter(mdl.ProfileVector.user_id == user_id).first()

    def save_embedding(self, user_id: int, embedding: np.ndarray, index_position: int):
        vector_bytes = pickle.dumps(embedding)
        profile_vector = mdl.ProfileVector(user_id=user_id, vector=vector_bytes, faiss_index_position=index_position)
        self.db.add(profile_vector)
        self.db.commit()
        self.db.refresh(profile_vector)
        return profile_vector

class RecomendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_recomendations(self, user_id: int, top_k: int = 5):
        profile_vector_record = self.db.query(mdl.ProfileVector).filter_by(user_id=user_id).first()
        
        if not profile_vector_record:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        embedding = pickle.loads(profile_vector_record.vector)
        query_vector = np.array([embedding], dtype="float32")
        
        distances, indices = faiss_index.search(query_vector, top_k * 3)

        user_faiss_pos = profile_vector_record.faiss_index_position
        recommended_positions = [int(idx) for idx in indices[0] if idx != user_faiss_pos] 

        if not recommended_positions:
            return []
        
        viewed_users = {int(uid) for uid in r.smembers(f"viewed:{user_id}")}


        recommended_user_ids = [
        user_id for (user_id,) in self.db.query(mdl.ProfileVector.user_id)
        .filter(
            mdl.ProfileVector.faiss_index_position.in_(recommended_positions),
            mdl.ProfileVector.user_id.notin_(viewed_users) 
        )
        .limit(top_k)
        .all()
    ]
        
        if not recommended_user_ids:
            r.delete(f"viewed:{user_id}")
            return []

        r.sadd(f"viewed:{user_id}", *map(str, recommended_user_ids))

        random.shuffle(recommended_user_ids)
        return self.db.query(mdl.User).filter(mdl.User.id.in_(recommended_user_ids)).all()

    

class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_my_posts(self, user_id: int):
        posts = self.db.query(mdl.Post).filter(mdl.Post.user_id == user_id).all()
        
        result = []
        for post in posts:
            images = self.db.query(mdl.PostImage.image).filter(mdl.PostImage.post_id == post.id).all()
            image_urls = [img[0] for img in images]  
            result.append({
                "id": post.id,
                "user_id": post.user_id,
                "text": post.text,
                "posted_at": post.posted_at,
                "images":  image_urls
            })
        
        return result
    
    def get_news(self, user_id: int, page: int = 1, limit: int = 5):
        connections = (
            self.db.query(mdl.Connection)
            .filter(mdl.Connection.user_id == user_id)
            .all()
        )

        target_ids = [connection.target_id for connection in connections]
        target_ids.append(user_id) 

        if not target_ids:
            return "Please add some friends"

        news = (
            self.db.query(mdl.Post)
            .filter(mdl.Post.user_id.in_(target_ids))
            .order_by(mdl.Post.posted_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        if not news:
            return "There are no news"
        
        result = []
        for post in news:
            images = self.db.query(mdl.PostImage.image).filter(mdl.PostImage.post_id == post.id).all()
            image_urls = [img[0] for img in images]  
            result.append({
                "id": post.id,
                "user_id": post.user_id,
                "text": post.text,
                "posted_at": post.posted_at,
                "images":  image_urls
            })

        return result
    
    def get_user_posts(self, user_id, current_user_id):
        connections = (
            self.db.query(mdl.Connection)
            .filter(mdl.Connection.user_id == current_user_id, mdl.Connection.target_id == user_id)
            .first()
        )

        if not connections:
            return HTTPException(status_code=401, detail="Unauthorized")

        return self.get_my_posts(user_id)

    
    def create_post(self, user_id: int, post_data: sch.PostCreate):
        post = mdl.Post(user_id = user_id, text=post_data.text)
        self.db.add(post)
        return post.id
    
    def delete_post(self, user_id: int, post_id: int):
        post = self.db.query(mdl.Post).filter(mdl.Post.user_id == user_id).filter(mdl.Post.id == post_id).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        self.db.delete(post)

        return post_id

    
    def create_image(self, post_id: int, images: List[str] = None):
        for path in images:
            post_image = mdl.PostImage(post_id=post_id, image=path)
            self.db.add(post_image)
        return "Images successfully add"

    def get_post_images(self, post_id: int):
        return self.db.query(mdl.PostImage).filter(mdl.PostImage.post_id == post_id).all()


class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_organizations(self):
        return self.db.query(mdl.Organization).all()
    
    def get_organization(self, organization_id: int):
        return self.db.query(mdl.Organization).filter(mdl.Organization.id == organization_id).first()
    
    def get_organizations_posts(self):
        return self.db.query(mdl.Post).filter(mdl.Post.organization_id.isnot(None)).all()

    def get_organization_posts(self, organization_id):
        return (
            self.db.query(mdl.Post).filter(mdl.Post.organization_id == organization_id).first()
        )
    
    def create_organization_posts(self, organization_id, president_id, post_data: sch.PostCreate):
        organization = self.db.query(mdl.Organization).filter(mdl.Organization.id == organization_id).first()
        if organization.president_id == president_id:
            post = mdl.Post(organization_id = organization_id, text=post_data.text)
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            return post
        return HTTPException(status_code=401, detail="Unauthorized")
        
    def delete_organization_post(self, post_id, president_id):
        post = self.db.query(mdl.Post).filter(mdl.Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        organization = self.db.query(mdl.Organization).filter(mdl.Organization.id == post.organization_id).first()
        if organization.president_id == president_id:
            self.db.delete(post)
            return post_id
        
        return HTTPException(status_code=401, detail="Unauthorized")
    
    def create_organization(self, organization_data: sch.Organization):
       
            organization = mdl.Organization(
                name=organization_data.name,
                image= organization_data.image,
                slogan=organization_data.slogan,
                description=organization_data.description,
                year=organization_data.year,
                president_id=organization_data.president_id
            )
            self.db.add(organization)

            return organization
        
        # except Exception as e:
        #     raise HTTPException(status_code=500, detail = "Internal Server error" )


        

class EventsRepository:
    def __init__(self, db: Session):
        self.db = db

    def results(self, events):
        grouped_events = defaultdict(list)

        for event in events:
            event_day = event.date.strftime("%Y-%m-%d") 
            grouped_events[event_day].append(event)
        return grouped_events

    def get_events(self):
        events = self.db.query(mdl.Event).order_by(mdl.Event.date).all()
        return self.results(events)
    
    def get_organization_events(self, organization_id):
        events = self.db.query(mdl.Event).filter(mdl.Event.organization_id == organization_id).all()

        return self.results(events)
    
    def delete_event(self, president_id, event_id):
        event = self.db.query(mdl.Event).filter(mdl.Event.id == event_id).first()
        if not event:
            return HTTPException(404, detail={"Event not found"})
        
        organization = self.db.query(mdl.Organization).filter(mdl.Organization.id == event.organization_id).first()

        if organization.president_id == president_id:
            self.db.delete(event)
            return event.id
        
        return HTTPException(status_code=401, detail="Unauthorized") 

        
    




def get_db():
    try:
        yield session
        session.commit()
    except:
        raise
    finally:
        session.close()

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_embedding_repository(db: Session = Depends(get_db)):
    return EmbeddingRepository(db)

def get_recomendation_repository(db: Session = Depends(get_db)):
    return RecomendationRepository(db)

def get_post_repository(db: Session = Depends(get_db)):
    return PostRepository(db)

def get_organization_repository(db: Session = Depends(get_db)):
    return OrganizationRepository(db)

def get_events_repository(db: Session = Depends(get_db)):
    return EventsRepository(db)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[2]
    else:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("userID")
        if user_id is None:
            raise HTTPException(status_code=401, detail="User Not Found")
        user = db.query(mdl.User).filter(mdl.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not Found")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token has expired, please login again")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
  