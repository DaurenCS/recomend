from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Base(BaseModel):
     
    class Config:
        from_attributes = True


class User(Base):
    id: int
    username: str
    email: str
    course: int
    faculty: str
    gender: str
    birthday: datetime
    bio: Optional[str] = ""
    
class PostBase(Base):
    text: Optional[str] = None


class PostCreate(PostBase):
    text: str 

class PostUpdate(PostBase):
    text: Optional[str] 

class PostImage(Base):
    id: int
    post_id: int
    image: str 

class Post(PostBase):
    id: int
    user_id: int
    posted_at: datetime
    images: List[str] = []



