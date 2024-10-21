from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from typing import Union, Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, String, DateTime, ForeignKey

data = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "owIbyag820022013",
    "database": "task_manager",
}

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{data['user']}:{data['password']}@{data['host']}:{data['port']}/{data['database']}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


class Base(DeclarativeBase):
    pass


# модель SQLAlchemy для пользователя
class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)


class Task(Base):
    __tablename__ = "task"

    task_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    important = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    heading = Column(String, nullable=True)
    task_text = Column(String, nullable=True)
    data_stop = Column(DateTime, nullable=True)
    prize = Column(String, nullable=True)


# Pydantic модель задачи
class TaskResponse(BaseModel):
    task_id:int
    user_id: int
    created_at: datetime
    important: bool = False
    completed: bool = False
    heading: Optional[str] = None
    task_text: Optional[str] = None
    data_stop: Optional[datetime] = None
    prize: Optional[str] = None

    class Config:
        orm_mode = True


# a это pydantic модель для валидации данных
class User(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    important: bool = False
    completed: bool = False
    heading: Optional[str] = None
    task_text: Optional[str] = None
    data_stop: Optional[datetime] = None
    prize: Optional[str] = None

    class Config:
        orm_mode = True


SessionLocal = sessionmaker(autoflush=False, bind=engine)
