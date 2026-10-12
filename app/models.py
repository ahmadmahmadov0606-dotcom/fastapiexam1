from datetime import datetime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,Integer,Float,DateTime,ForeignKey
from database import Base


class User(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100),nullable=False)
    email:Mapped[str]=mapped_column(String(100),nullable=False)

    orders=relationship('Order')
    favorites=relationship('Favorite')
