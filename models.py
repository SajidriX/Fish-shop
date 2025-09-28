from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./fishing.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    balance = Column(Integer, default=0)
    password = Column(String)
    role = Column(String, default="user")

class Fishes(Base):
    __tablename__ = "fishes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    cathced = Column(String)


def init_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
