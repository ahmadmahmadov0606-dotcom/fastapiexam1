from datetime import datetime
from pydantic import BaseModel,ConfigDict,Field


class UserCreate(BaseModel):
    name:str
    email:str

class UserRead(UserCreate):
    id:int

    model_config=ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name:str

class CategoryRead(CategoryCreate):
    id:int

    model_config=ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name:str
    price:float=Field(gt=0)
    stock:int=Field(ge=0)
    category_id:int

class ProductRead(ProductCreate):
    id:int
    category:CategoryRead

    model_config=ConfigDict(from_attributes=True)


class CartAdd(BaseModel):
    user_id:int
    product_id:int
    quantity:int=Field(ge=1)

class CartUpdate(BaseModel):
    quantity:int=Field(ge=1)


class OrderCreate(BaseModel):
    user_id:int

class OrderStatus(BaseModel):
    status:str=Field(pattern='^(new|paid|cancelled)$')

class OrderItemRead(BaseModel):
    quantity:int
    price:float
    product:ProductRead

    model_config=ConfigDict(from_attributes=True)

class OrderRead(BaseModel):
    id:int
    user_id:int
    total:float
    status:str
    created_at:datetime
    items:list[OrderItemRead]

    model_config=ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    user_id:int
    rating:int=Field(ge=1,le=5)
    text:str

class ReviewRead(ReviewCreate):
    id:int
    product_id:int

    model_config=ConfigDict(from_attributes=True)


class FavoriteCreate(BaseModel):
    user_id:int
    product_id:int

class FavoriteRead(BaseModel):
    id:int
    product:ProductRead

    model_config=ConfigDict(from_attributes=True)
