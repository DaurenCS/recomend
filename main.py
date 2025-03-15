from app.models import schemas as sch
from fastapi import FastAPI, HTTPException, Depends
from app.repositories.Repository import *
from app.services.generateEmbedding import *
from app.services.embeddingService import EmbeddingService, get_embedding_service
import app.models.models as mdl
from fastapi import File, UploadFile
import shutil
from fastapi.responses import FileResponse

UPLOAD_DIR = "uploads/"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = FastAPI()

@app.post("/generate_embedding/{user_id}")
def generate_and_store_embedding(user_id: int, 
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
def get_recomendation_user(user_id: int, top_k: int = 5 ,  service: RecomendationRepository = Depends(get_recomendation_repository)):
    recomendation_users = service.get_recomendations(user_id, top_k)
    return  [sch.User.model_validate(user) for user in recomendation_users]

@app.get("/users")
def get_users(service: UserRepository = Depends(get_user_repository)):
    users = service.get_users()
    return [sch.User.model_validate(user) for user in users]

@app.get("/users/{user_id}")
def get_user(user_id: int, service: UserRepository = Depends(get_user_repository)):
    user = service.get_user(user_id)
    return sch.User.model_validate(user)


@app.get("/my_posts")
def get_my_posts(current_user: mdl.User = Depends(get_current_user),
                 service: PostRepository = Depends(get_post_repository)):
    posts = service.get_my_posts(current_user.id)
    return [sch.Post.model_validate(post) for post in posts]

@app.get('/news')
def get_news(current_user: mdl.User = Depends(get_current_user), service: PostRepository = Depends(get_post_repository)):
    news = service.get_news(current_user.id)
    
    return news


@app.post("/posts")
async def create_posts(post_data: sch.PostCreate,
                       current_user: mdl.User = Depends(get_current_user), 
                       service: PostRepository = Depends(get_post_repository)):
    
    return service.create_post(current_user.id, post_data )
    
@app.post("/posts/{post_id}/upload")
async def upload_file(post_id: int, images: List[UploadFile] = File(...),
                      service: PostRepository = Depends(get_post_repository)):
    image_paths = []
    for image in images:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_paths.append(file_path)
    return service.create_image(post_id, image_paths)
    

    
@app.get("/posts/{post_id}/images", response_model=List[sch.PostImage])
def get_post_images(post_id: int, service: PostRepository = Depends(get_post_repository)):
    return service.get_post_images(post_id)

@app.get("/images/{filename}")
async def get_image(filename: str):
    return FileResponse(f"uploads/{filename}")
    