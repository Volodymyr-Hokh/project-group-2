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
from sqlalchemy.orm import declarative_base


Base = declarative_base()

image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("note", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())


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
    username = Column(String)
    password = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    role = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean)


class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
