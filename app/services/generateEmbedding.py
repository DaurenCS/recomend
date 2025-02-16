import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from app.repositories.Repository import *
from app.services.generateEmbedding import *


class ProfileMLP(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, output_dim=128):
        super(ProfileMLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x



faculty_mapping = {"SEOGI":0, "SG":1, "SITE":2, "BS":3, "ISE":4, "KMA":5, "SAM":6, "SCE":7, "SSS":8, "SMSGT":9}
course_mapping = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
gender_mapping = {"Male": 0, "Female": 1, "Other": 2}


text_model = SentenceTransformer('all-MiniLM-L6-v2')


text_embedding_dim = 64  
input_dim = len(faculty_mapping) + len(course_mapping) + len(gender_mapping) + text_embedding_dim + 1  # +1 для нормализованного возраста
mlp_model = ProfileMLP(input_dim)
mlp_model.eval()

def generate_embedding(user):
    # One-Hot кодирование категориальных признаков
    faculty_one_hot = np.eye(len(faculty_mapping))[faculty_mapping.get(user.get('faculty'), 0)]
    course_one_hot = np.eye(len(course_mapping))[course_mapping.get(user.get('course'), 0)]
    gender_one_hot = np.eye(len(gender_mapping))[gender_mapping.get(user.get('gender'), 0)]
    
    # Генерация эмбеддинга для биографии (bio)
    bio_text = user.get('bio', "")
    if bio_text is None:
        bio_text = ""
    interests_emb_full = text_model.encode([bio_text])
    interests_emb = interests_emb_full[0][:text_embedding_dim]
    

    # Нормализация возраста (предполагается, что возраст указан)
    age_normalized = np.array([user.get('age', 0) / 100.0])
    
    # Конкатенация всех признаков
    input_vector = np.concatenate([faculty_one_hot, course_one_hot, gender_one_hot, interests_emb, age_normalized])
    input_tensor = torch.from_numpy(input_vector).float().unsqueeze(0)
    with torch.no_grad():
        embedding = mlp_model(input_tensor).numpy().squeeze()
    return embedding