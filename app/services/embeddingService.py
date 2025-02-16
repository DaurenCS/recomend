from app.services.generateEmbedding import generate_embedding
import os
import numpy as np
import faiss
from fastapi import HTTPException, Depends
import numpy as np
from app.repositories.Repository import get_embedding_repository, EmbeddingRepository

embedding_dim = 128
faiss_index_file = "faiss.index"
if os.path.exists(faiss_index_file):
    faiss_index = faiss.read_index(faiss_index_file)
else:
    faiss_index = faiss.IndexFlatL2(embedding_dim)

def save_faiss_index():
    """Сохраняем Faiss-индекс на диск для персистентности."""
    faiss.write_index(faiss_index, faiss_index_file)

class EmbeddingService:
    def __init__(self, repository: EmbeddingRepository):
        self.repository = repository
    
    

    def generate_and_store_embedding(self, user_id: int, user_data: dict):
        if self.repository.get_embedding(user_id):
            raise HTTPException(status_code=400, detail="Пользователь уже существует")

        embedding = generate_embedding(user_data)
        embedding_np = np.array([embedding]).astype("float32")
        faiss_index.add(embedding_np)
        index_position = faiss_index.ntotal - 1
        save_faiss_index()

        return self.repository.save_embedding(user_id, embedding, index_position)
    


def get_embedding_service(repository: EmbeddingRepository = Depends(get_embedding_repository)):
    return EmbeddingService(repository)