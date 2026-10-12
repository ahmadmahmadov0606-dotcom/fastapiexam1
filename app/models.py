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


class Category(Base):
    __tablename__='categories'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100),nullable=False)

    products=relationship('Product',back_populates='category')


class Product(Base):
    __tablename__='products'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(150),nullable=False)
    price:Mapped[float]=mapped_column(Float,nullable=False)
    stock:Mapped[int]=mapped_column(Integer,nullable=False)
    category_id:Mapped[int]=mapped_column(ForeignKey('categories.id'),nullable=False)

    category=relationship('Category',back_populates='products')
    reviews=relationship('Review')


class CartItem(Base):
    __tablename__='cart_items'
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),nullable=False)
    product_id:Mapped[int]=mapped_column(ForeignKey('products.id'),nullable=False)
    quantity:Mapped[int]=mapped_column(Integer,nullable=False)

    product=relationship('Product')


class Order(Base):
    __tablename__='orders'
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),nullable=False)
    total:Mapped[float]=mapped_column(Float,nullable=False)
    status:Mapped[str]=mapped_column(String(20),default='new')
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.now)

    items=relationship('OrderItem')


class OrderItem(Base):
    __tablename__='order_items'
    id:Mapped[int]=mapped_column(primary_key=True)
    order_id:Mapped[int]=mapped_column(ForeignKey('orders.id'),nullable=False)
    product_id:Mapped[int]=mapped_column(ForeignKey('products.id'),nullable=False)
    quantity:Mapped[int]=mapped_column(Integer,nullable=False)
    price:Mapped[float]=mapped_column(Float,nullable=False)

    product=relationship('Product')
