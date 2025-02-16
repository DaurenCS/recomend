from sqlalchemy import  Column, Integer, String
from database.database import Base
from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, func, ForeignKey
from datetime import date

_id = Annotated[int, mapped_column(Integer, primary_key=True)]

class User(Base):
    __tablename__ = "users"

    id: Mapped[_id]
    username = Column(String, index=True)
    email = Column(String, index=True)
    faculty: Mapped[str] = mapped_column(String, nullable=False)
    course: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[str] = mapped_column(String, nullable=True)
    birthday =  mapped_column(DateTime)

    @property
    def age(self) -> int:
        """Вычисляет возраст на основе даты рождения."""
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

class ProfileVector(Base):
    __tablename__ = "profile_vectors"
    
    id: Mapped[_id]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    vector = mapped_column(LargeBinary)
    faiss_index_position = Column(Integer, nullable=True)
    created_at = mapped_column(DateTime, default=func.now())