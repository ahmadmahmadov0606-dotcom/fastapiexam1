from datetime import datetime
from pydantic import BaseModel,ConfigDict,Field


class UserCreate(BaseModel):
    name:str
    email:str

class UserRead(UserCreate):
    id:int

    model_config=ConfigDict(from_attributes=True)
