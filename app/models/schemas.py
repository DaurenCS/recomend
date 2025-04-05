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
    likes: int

class CreateOrganization(Base):
    name: str
    slogan: str
    description: str
    image: str
    year: int
    president_id: int

class Organization(Base):
    id: int
    name: str
    image: str
    slogan: str
    description: str
    year: int
    president_id: int

class EventCreate(Base):
    name: str
    organization_id: int
    date: datetime
    location: str
    description: str
    price: int
    additional: str

class EventResponse(EventCreate):
    id: int
    created_at: datetime

class Like(Base):
    post_id: int

class Tag(Base):
    id: int
    name: str

class createUserTags(Base):
    user_id: int
    tags_id: List[int] 