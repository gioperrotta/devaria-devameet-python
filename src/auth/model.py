from sqlalchemy import Column, Integer, String
from src.core.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, index=True, unique=True)
    hashed_password = Column(String(100), nullable=False)

