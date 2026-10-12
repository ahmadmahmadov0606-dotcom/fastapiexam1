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


@app.post('/cart/add/')
def add_to_cart(data:schemas.CartAdd,db:Session=Depends(get_db)):
    return crud.add_to_cart(db,data)

@app.get('/cart/{user_id}')
def get_cart(user_id:int,db:Session=Depends(get_db)):
    return crud.get_cart(db,user_id)

@app.put('/cart/items/{cart_item_id}')
def update_cart_item(cart_item_id:int,data:schemas.CartUpdate,db:Session=Depends(get_db)):
    return crud.update_cart_item(db,cart_item_id,data)

@app.delete('/cart/items/{cart_item_id}')
def delete_cart_item(cart_item_id:int,db:Session=Depends(get_db)):
    return crud.delete(db,crud.get_or_404(db,models.CartItem,cart_item_id))

@app.delete('/cart/clear/{user_id}')
def clear_cart(user_id:int,db:Session=Depends(get_db)):
    return crud.clear_cart(db,user_id)


@app.post('/orders/create/',response_model=schemas.OrderRead)
def create_order(data:schemas.OrderCreate,db:Session=Depends(get_db)):
    return crud.create_order(db,data)

@app.get('/orders/',response_model=list[schemas.OrderRead])
def get_orders(
    status:str|None=None,
    sort_by:str|None=None,
    skip:int=0,
    limit:int=10,
    db:Session=Depends(get_db)
):
    return crud.get_orders(db,status,sort_by,skip,limit)

@app.get('/orders/{order_id}',response_model=schemas.OrderRead)
def get_order(order_id:int,db:Session=Depends(get_db)):
    return crud.get_or_404(db,models.Order,order_id)

@app.put('/orders/{order_id}',response_model=schemas.OrderRead)
def change_status(order_id:int,data:schemas.OrderStatus,db:Session=Depends(get_db)):
    return crud.change_status(db,order_id,data)


@app.post('/favorites/',response_model=schemas.FavoriteRead)
def add_favorite(data:schemas.FavoriteCreate,db:Session=Depends(get_db)):
    return crud.add_favorite(db,data)

@app.get('/favorites/{user_id}',response_model=list[schemas.FavoriteRead])
def get_favorites(user_id:int,db:Session=Depends(get_db)):
    return crud.get_or_404(db,models.User,user_id).favorites

@app.delete('/favorites/{favorite_id}')
def delete_favorite(favorite_id:int,db:Session=Depends(get_db)):
    return crud.delete(db,crud.get_or_404(db,models.Favorite,favorite_id))
