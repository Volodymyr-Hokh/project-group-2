from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Table,
    func,
)
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum

Base = declarative_base()

image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    public_id = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return self.name


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_id = Column(Integer, ForeignKey("images.id"))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    confirmed = Column(Boolean, default=False)
    created_at = Column("created_at", DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')
    
