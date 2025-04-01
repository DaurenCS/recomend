from sqlalchemy import  Column, Integer, String
from database.database import Base
from typing import Annotated, List
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, func, ForeignKey, UniqueConstraint
from datetime import date
from sqlalchemy.dialects.postgresql import UUID

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
    image_uuid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True, default=uuid.uuid4)
    
    posts: Mapped['Post'] = relationship(back_populates='user', cascade="all, delete-orphan")
    organization: Mapped['Organization'] = relationship(back_populates='president')
    likes: Mapped['Like'] = relationship(back_populates="user", cascade="all, delete-orphan")
    tags: Mapped[List['Tag']] = relationship(secondary="user_tags", backref="users")


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

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[_id]
    posted_at  = mapped_column(DateTime, default=func.now())
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    text: Mapped[str] = mapped_column(String, nullable=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'), nullable=True)
    
    organization: Mapped['Organization'] = relationship(back_populates='post')
    post_images: Mapped[List['PostImage']] = relationship(back_populates='post', cascade="all, delete-orphan", passive_deletes=True, lazy="joined")
    user: Mapped['User'] = relationship(back_populates='posts')
    likes: Mapped[List['Like']] = relationship(back_populates="post", cascade="all, delete-orphan")

class PostImage(Base):
    __tablename__ = "post_images"
    
    id: Mapped[_id]
    post_id : Mapped[int] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'))
    image : Mapped[str] = mapped_column(String, nullable=True)

    post: Mapped['Post'] = relationship(back_populates='post_images',  passive_deletes=True)


class Connection(Base):
    __tablename__ = 'connections'

    id: Mapped[_id]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    target_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
 

    # user: Mapped['User'] = relationship(back_populates='connection')


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[_id]
    name = Column(String, index=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    slogan: Mapped[str]
    description: Mapped[str]
    year = Column(Integer, nullable=True)
    president_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    president: Mapped['User'] = relationship(back_populates='organization')
    events: Mapped['Event'] = relationship(back_populates='organization')
    post: Mapped['Post'] = relationship(back_populates='organization')


class Event(Base):
    __tablename__ = "organization_events"

    id: Mapped[_id]
    name: Mapped[str]
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'))
    created_at = Column(DateTime, default=func.now())
    date = mapped_column(DateTime)
    location: Mapped[str]
    image: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str]
    price: Mapped[int]
    additional: Mapped[str]

    organization: Mapped['Organization'] = relationship(back_populates='events')


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["Post"] = relationship(back_populates="likes")
    
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class UserTag(Base):
    __tablename__ = "user_tags"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


