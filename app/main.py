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


@app.post('/products/',response_model=schemas.ProductRead)
def create_product(data:schemas.ProductCreate,db:Session=Depends(get_db)):
    crud.get_or_404(db,models.Category,data.category_id)
    return crud.create(db,models.Product(**data.model_dump()))

@app.get('/products/',response_model=list[schemas.ProductRead])
def get_products(
    search:str|None=None,
    category_id:int|None=None,
    min_price:float|None=None,
    max_price:float|None=None,
    sort_by:str|None=None,
    skip:int=0,
    limit:int=10,
    db:Session=Depends(get_db)
):
    return crud.get_products(db,search,category_id,min_price,max_price,sort_by,skip,limit)

@app.get('/products/{product_id}',response_model=schemas.ProductRead)
def get_product(product_id:int,db:Session=Depends(get_db)):
    return crud.get_or_404(db,models.Product,product_id)

@app.put('/products/{product_id}',response_model=schemas.ProductRead)
def update_product(product_id:int,data:schemas.ProductCreate,db:Session=Depends(get_db)):
    crud.get_or_404(db,models.Category,data.category_id)
    return crud.update(db,crud.get_or_404(db,models.Product,product_id),data)

@app.delete('/products/{product_id}')
def delete_product(product_id:int,db:Session=Depends(get_db)):
    return crud.delete_product(db,product_id)


@app.post('/products/{product_id}/reviews/',response_model=schemas.ReviewRead)
def create_review(product_id:int,data:schemas.ReviewCreate,db:Session=Depends(get_db)):
    crud.get_or_404(db,models.Product,product_id)
    crud.get_or_404(db,models.User,data.user_id)
    return crud.create(db,models.Review(product_id=product_id,**data.model_dump()))

@app.get('/products/{product_id}/reviews/',response_model=list[schemas.ReviewRead])
def get_reviews(product_id:int,db:Session=Depends(get_db)):
    return crud.get_or_404(db,models.Product,product_id).reviews
