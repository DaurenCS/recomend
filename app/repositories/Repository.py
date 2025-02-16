from fastapi import Depends
import app.models.models as mdl
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from database.database import session
import pickle
import os
import faiss

import numpy as np

import redis

r = redis.Redis(
    host="redis-17009.c8.us-east-1-2.ec2.redns.redis-cloud.com",  
    port=17009,  
    password="zd66qejs39E8MbD1QLx3QlLwtH3F7BEB",  # Add password if required
    db=0,  
    decode_responses=True  
)

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
        
        distances, indices = faiss_index.search(query_vector, top_k * 10)

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
            return []

        r.sadd(f"viewed:{user_id}", *map(str, recommended_user_ids))

        return self.db.query(mdl.User).filter(mdl.User.id.in_(recommended_user_ids)).all()

    

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
