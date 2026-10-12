from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import schemas


def get_or_404(db:Session,model,pk:int):
    obj=db.get(model,pk)
    if not obj:
        raise HTTPException(status_code=404,detail='Not found')
    return obj

def create(db:Session,obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db:Session,obj,data):
    for key,value in data.model_dump().items():
        setattr(obj,key,value)
    db.commit()
    db.refresh(obj)
    return obj

def delete(db:Session,obj):
    db.delete(obj)
    db.commit()
    return {'message':'deleted'}


def user_statistics(db:Session,user_id:int):
    user=get_or_404(db,models.User,user_id)
    orders=[o for o in user.orders if o.status!='cancelled']
    return {
        'orders_count':len(orders),
        'total_spent':sum(o.total for o in orders)
    }


def get_products(db:Session,search,category_id,min_price,max_price,sort_by,skip,limit):
    query=db.query(models.Product)
    if search:
        query=query.filter(models.Product.name.ilike(f'%{search}%'))
    if category_id:
        query=query.filter(models.Product.category_id==category_id)
    if min_price:
        query=query.filter(models.Product.price>=min_price)
    if max_price:
        query=query.filter(models.Product.price<=max_price)
    if sort_by=='price':
        query=query.order_by(models.Product.price)
    if sort_by=='name':
        query=query.order_by(models.Product.name)
    return query.offset(skip).limit(limit).all()


def get_cart(db:Session,user_id:int):
    get_or_404(db,models.User,user_id)
    items=db.query(models.CartItem).filter(models.CartItem.user_id==user_id).all()
    result=[]
    for item in items:
        result.append({
            'id':item.id,
            'product':item.product.name,
            'price':item.product.price,
            'quantity':item.quantity,
            'subtotal':item.product.price*item.quantity
        })
    return {'items':result,'total':sum(i['subtotal'] for i in result)}

def add_to_cart(db:Session,data:schemas.CartAdd):
    get_or_404(db,models.User,data.user_id)
    product=get_or_404(db,models.Product,data.product_id)
    item=db.query(models.CartItem).filter(
        models.CartItem.user_id==data.user_id,
        models.CartItem.product_id==data.product_id
    ).first()
    if item:
        item.quantity+=data.quantity
    else:
        item=models.CartItem(**data.model_dump())
        db.add(item)
    if item.quantity>product.stock:
        raise HTTPException(status_code=400,detail='Not enough stock')
    db.commit()
    return get_cart(db,data.user_id)

def update_cart_item(db:Session,cart_item_id:int,data:schemas.CartUpdate):
    item=get_or_404(db,models.CartItem,cart_item_id)
    if data.quantity>item.product.stock:
        raise HTTPException(status_code=400,detail='Not enough stock')
    item.quantity=data.quantity
    db.commit()
    return get_cart(db,item.user_id)

def clear_cart(db:Session,user_id:int):
    db.query(models.CartItem).filter(models.CartItem.user_id==user_id).delete()
    db.commit()
    return {'message':'cart cleared'}


def create_order(db:Session,data:schemas.OrderCreate):
    get_or_404(db,models.User,data.user_id)
    items=db.query(models.CartItem).filter(models.CartItem.user_id==data.user_id).all()
    if not items:
        raise HTTPException(status_code=400,detail='Cart is empty')
    order=models.Order(user_id=data.user_id,total=0)
    for item in items:
        if item.quantity>item.product.stock:
            raise HTTPException(status_code=400,detail='Not enough stock')
        order.items.append(models.OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        ))
        order.total+=item.product.price*item.quantity
        item.product.stock-=item.quantity
        db.delete(item)
    return create(db,order)
