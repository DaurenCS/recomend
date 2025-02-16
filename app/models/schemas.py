from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    
    
