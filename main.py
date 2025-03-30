from app.models import schemas as sch
from fastapi import FastAPI, HTTPException, Depends
from app.repositories.Repository import *
from app.services.generateEmbedding import *
from app.services.embeddingService import EmbeddingService, get_embedding_service
import app.models.models as mdl
from fastapi import File, UploadFile
import shutil
from fastapi.responses import FileResponse
from dotenv import load_dotenv


load_dotenv()


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/generate_embedding/{user_id}")
async def generate_and_store_embedding(user_id: int, 
                                    service: EmbeddingService = Depends(get_embedding_service),
                                    user_repo: UserRepository = Depends(get_user_repository)):
    
    user = user_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    
    service.generate_and_store_embedding(user.id, {
        "faculty": user.faculty,
        "course": user.course,
        "gender": user.gender,
        "bio": user.bio,
        "age": user.age
    })
    return {"message": "Эмбеддинг сгенерирован и сохранён", "user_id": user_id}

@app.get("/recomendation/{user_id}")
async def get_recomendation_user(user_id: int, top_k: int = 5 ,  service: RecomendationRepository = Depends(get_recomendation_repository)):
    recomendation_users = service.get_recomendations(user_id, top_k)
    return  [sch.User.model_validate(user) for user in recomendation_users]

@app.get("/users")
async def get_users(service: UserRepository = Depends(get_user_repository)):
    users = service.get_users()
    return [sch.User.model_validate(user) for user in users]

@app.get("/users/{user_id}")
async def get_user(user_id: int, service: UserRepository = Depends(get_user_repository)):
    user = service.get_user(user_id)
    return sch.User.model_validate(user)

@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int, service: PostRepository = Depends(get_post_repository), 
                   current_user: mdl.User = Depends(get_current_user)):
    
    return service.get_user_posts(user_id, current_user.id)


@app.get('/news')
async def get_news(current_user: mdl.User = Depends(get_current_user), 
            service: PostRepository = Depends(get_post_repository), page: int = 1, limit: int = 5):
    news = service.get_news(current_user.id, page, limit)
    
    return news

@app.get("/posts")
async def get_my_posts(current_user: mdl.User = Depends(get_current_user),
                 service: PostRepository = Depends(get_post_repository)):
    posts = service.get_posts(current_user.id)
    return posts

@app.post("/posts")
async def create_posts(post_data: sch.PostCreate,
                       current_user: mdl.User = Depends(get_current_user), 
                       service: PostRepository = Depends(get_post_repository)):
    
    return service.create_post(current_user.id, post_data)

@app.delete('/posts')
async def delete_post(post_id: int,
                      current_user: mdl.User = Depends(get_current_user),
                      service: PostRepository = Depends(get_post_repository)):
    
    return service.delete_post(current_user.id, post_id)
    
@app.post("/posts/{post_id}/upload")
async def upload_file(
    post_id: int, 
    images: List[UploadFile] = File(...),
    curren_user: mdl.User = Depends(get_current_user),
    service: PostRepository = Depends(get_post_repository)
):
    return await service.create_image(post_id, curren_user.id, images)

    
@app.get("/posts/{post_id}/images", response_model=List[sch.PostImage])
def get_post_images(post_id: int, service: PostRepository = Depends(get_post_repository)):
    return service.get_post_images(post_id)

@app.get("/uploads/{filename}")
async def get_image(filename: str):
    return FileResponse(f"uploads/{filename}")


@app.get("/organizations")
async def get_organizations(service: OrganizationRepository = Depends(get_organization_repository)):
    return service.get_organizations()


@app.get("/organization/{organization_id}")
async def get_organization(organization_id: int, service: OrganizationRepository = Depends(get_organization_repository)):
    return service.get_organization(organization_id)

@app.get("/organization/{organization_id}/posts")
def get_organization_posts(organization_id: int, service: OrganizationRepository = Depends(get_organization_repository)):
    return service.get_organization_posts(organization_id)

@app.get("/organization/{organization_id}/events")
def get_organization_events(organization_id: int , service: EventsRepository = Depends(get_events_repository)):
    return service.get_organization_events(organization_id)

@app.post("/organization/posts")
def create_organization_post(organization_id: int, 
                             post_data: sch.PostCreate,
                             service: OrganizationRepository = Depends(get_organization_repository),
                             current_user: mdl.User = Depends(get_current_user)):
    
    return service.create_organization_posts(organization_id, current_user.id, post_data)

@app.get("/organizations/posts")
def get_organizations_post(service: OrganizationRepository = Depends(get_organization_repository)):
    return service.get_organizations_posts()


@app.delete("/organization/posts/{post_id}")
def delete_organization_post(post_id:int,
                             service: OrganizationRepository = Depends(get_organization_repository),
                             current_user: mdl.User = Depends(get_current_user)):
    return service.delete_organization_post(post_id, current_user.id)

@app.post("/events")
def create_events(organization_id: int,
                  event_data: sch.EventCreate,
                  service: EventsRepository = Depends(get_events_repository),
                  current_user: mdl.User = Depends(get_current_user),     
                  ):
    return service.create_event(current_user.id, organization_id, event_data)

@app.get("/events")
def get_events(service: EventsRepository = Depends(get_events_repository)):
    return service.get_events()

@app.delete("/event/{event_id}")
def delete_event(event_id: int, service: EventsRepository = Depends(get_events_repository),
                 current_user: mdl.User = Depends(get_current_user)):
    return service.delete_event(current_user.id, event_id)

@app.post("/like")
def like_post(like_data: sch.Like,
              current_user: mdl.User = Depends(get_current_user),
              service: PostRepository = Depends(get_post_repository)
              ):
    return service.like_post(like_data, current_user.id)


# @app.post("/organizations")
# async def create_organization(organization_data: sch.CreateOrganization, 
#                               service: OrganizationRepository = Depends(get_organization_repository)):
#     return service.create_organization(organization_data)
    