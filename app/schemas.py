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
