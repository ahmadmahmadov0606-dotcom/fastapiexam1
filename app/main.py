from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db,engine,Base
import models
import schemas
import crud

Base.metadata.create_all(bind=engine)

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.post('/users/',response_model=schemas.UserRead)
def create_user(data:schemas.UserCreate,db:Session=Depends(get_db)):
    return crud.create(db,models.User(**data.model_dump()))

@app.get('/users/',response_model=list[schemas.UserRead])
def get_users(db:Session=Depends(get_db)):
    return db.query(models.User).all()

@app.get('/users/{user_id}',response_model=schemas.UserRead)
def get_user(user_id:int,db:Session=Depends(get_db)):
    return crud.get_or_404(db,models.User,user_id)

@app.put('/users/{user_id}',response_model=schemas.UserRead)
def update_user(user_id:int,data:schemas.UserCreate,db:Session=Depends(get_db)):
    return crud.update(db,crud.get_or_404(db,models.User,user_id),data)

@app.delete('/users/{user_id}')
def delete_user(user_id:int,db:Session=Depends(get_db)):
    return crud.delete(db,crud.get_or_404(db,models.User,user_id))

@app.get('/users/{user_id}/orders/',response_model=list[schemas.OrderRead])
def user_orders(user_id:int,db:Session=Depends(get_db)):
    return crud.get_or_404(db,models.User,user_id).orders

@app.get('/users/{user_id}/statistics/')
def user_statistics(user_id:int,db:Session=Depends(get_db)):
    return crud.user_statistics(db,user_id)


@app.post('/categories/',response_model=schemas.CategoryRead)
def create_category(data:schemas.CategoryCreate,db:Session=Depends(get_db)):
    return crud.create(db,models.Category(**data.model_dump()))

@app.get('/categories/',response_model=list[schemas.CategoryRead])
def get_categories(db:Session=Depends(get_db)):
    return db.query(models.Category).all()

@app.get('/categories/{category_id}',response_model=schemas.CategoryRead)
def get_category(category_id:int,db:Session=Depends(get_db)):
    return crud.get_or_404(db,models.Category,category_id)

@app.put('/categories/{category_id}',response_model=schemas.CategoryRead)
def update_category(category_id:int,data:schemas.CategoryCreate,db:Session=Depends(get_db)):
    return crud.update(db,crud.get_or_404(db,models.Category,category_id),data)

@app.delete('/categories/{category_id}')
def delete_category(category_id:int,db:Session=Depends(get_db)):
    return crud.delete(db,crud.get_or_404(db,models.Category,category_id))
