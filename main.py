from app.models import schemas as sch
from fastapi import FastAPI, HTTPException, Depends
from app.repositories.Repository import *
from app.services.generateEmbedding import *
from app.services.embeddingService import EmbeddingService, get_embedding_service




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


