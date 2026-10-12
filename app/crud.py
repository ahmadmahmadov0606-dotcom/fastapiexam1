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

def update_user(db:Session,user_id:int,data:schemas.UserCreate):
    user=get_or_404(db,models.User,user_id)
    user.name=data.name
    user.email=data.email
    db.commit()
    db.refresh(user)
    return user

def update_category(db:Session,category_id:int,data:schemas.CategoryCreate):
    category=get_or_404(db,models.Category,category_id)
    category.name=data.name
    db.commit()
    db.refresh(category)
    return category

def update_product(db:Session,product_id:int,data:schemas.ProductCreate):
    product=get_or_404(db,models.Product,product_id)
    get_or_404(db,models.Category,data.category_id)
    product.name=data.name
    product.price=data.price
    product.stock=data.stock
    product.category_id=data.category_id
    db.commit()
    db.refresh(product)
    return product

def delete(db:Session,obj):
    db.delete(obj)
    db.commit()
    return {'message':'deleted'}


def user_statistics(db:Session,user_id:int):
    user=get_or_404(db,models.User,user_id)
    count=0
    total=0
    for order in user.orders:
        if order.status!='cancelled':
            count+=1
            total+=order.total
    return {'orders_count':count,'total_spent':total}


def user_purchases(db:Session,user_id:int):
    user=get_or_404(db,models.User,user_id)
    result=[]
    for order in user.orders:
        if order.status!='cancelled':
            for item in order.items:
                result.append({'order_id':order.id,'product':item.product.name,'quantity':item.quantity,'price':item.price})
    return result

def user_products(db:Session,user_id:int):
    products={}
    for item in user_purchases(db,user_id):
        products[item['product']]=products.get(item['product'],0)+item['quantity']
    return products

def last_order(db:Session,user_id:int):
    get_or_404(db,models.User,user_id)
    order=db.query(models.Order).filter_by(user_id=user_id).order_by(models.Order.created_at.desc()).first()
    if not order:
        raise HTTPException(status_code=404,detail='No orders')
    return order

def most_expensive_order(db:Session,user_id:int):
    get_or_404(db,models.User,user_id)
    order=db.query(models.Order).filter_by(user_id=user_id).order_by(models.Order.total.desc()).first()
    if not order:
        raise HTTPException(status_code=404,detail='No orders')
    return order


def get_products(db:Session,search,category_id,min_price,max_price,sort_by,skip,limit):
    query=db.query(models.Product)
    if search:
        query=query.filter(models.Product.name.ilike(f'%{search}%'))
    if category_id:
        query=query.filter_by(category_id=category_id)
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
    items=db.query(models.CartItem).filter_by(user_id=user_id).all()
    result=[]
    total=0
    for item in items:
        subtotal=item.product.price*item.quantity
        total+=subtotal
        result.append({'id':item.id,'product':item.product.name,'quantity':item.quantity,'subtotal':subtotal})
    return {'items':result,'total':total}

def add_to_cart(db:Session,data:schemas.CartAdd):
    get_or_404(db,models.User,data.user_id)
    product=get_or_404(db,models.Product,data.product_id)
    item=db.query(models.CartItem).filter_by(user_id=data.user_id,product_id=data.product_id).first()
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
    db.query(models.CartItem).filter_by(user_id=user_id).delete()
    db.commit()
    return {'message':'cart cleared'}


def create_order(db:Session,data:schemas.OrderCreate):
    get_or_404(db,models.User,data.user_id)
    items=db.query(models.CartItem).filter_by(user_id=data.user_id).all()
    if not items:
        raise HTTPException(status_code=400,detail='Cart is empty')
    order=models.Order(user_id=data.user_id,total=0)
    for item in items:
        if item.quantity>item.product.stock:
            raise HTTPException(status_code=400,detail='Not enough stock')
        order.items.append(models.OrderItem(product_id=item.product_id,quantity=item.quantity,price=item.product.price))
        order.total+=item.product.price*item.quantity
        item.product.stock-=item.quantity
        db.delete(item)
    return create(db,order)

def get_orders(db:Session,status,sort_by,skip,limit):
    query=db.query(models.Order)
    if status:
        query=query.filter_by(status=status)
    if sort_by=='total':
        query=query.order_by(models.Order.total)
    if sort_by=='date':
        query=query.order_by(models.Order.created_at)
    return query.offset(skip).limit(limit).all()

def change_status(db:Session,order_id:int,status:str):
    order=get_or_404(db,models.Order,order_id)
    if status not in ['new','paid','cancelled']:
        raise HTTPException(status_code=400,detail='Wrong status')
    if order.status=='cancelled':
        raise HTTPException(status_code=400,detail='Order is cancelled')
    if status=='cancelled':
        for item in order.items:
            item.product.stock+=item.quantity
    order.status=status
    db.commit()
    db.refresh(order)
    return order


def delete_product(db:Session,product_id:int):
    product=get_or_404(db,models.Product,product_id)
    active=db.query(models.OrderItem).join(models.Order).filter_by(status='new').filter(models.OrderItem.product_id==product_id).first()
    if active:
        raise HTTPException(status_code=400,detail='Product is in active order')
    return delete(db,product)


def add_favorite(db:Session,data:schemas.FavoriteCreate):
    get_or_404(db,models.User,data.user_id)
    get_or_404(db,models.Product,data.product_id)
    if is_favorite(db,data.user_id,data.product_id):
        raise HTTPException(status_code=400,detail='Already in favorites')
    return create(db,models.Favorite(**data.model_dump()))


def is_favorite(db:Session,user_id:int,product_id:int):
    return db.query(models.Favorite).filter_by(user_id=user_id,product_id=product_id).first()

def delete_favorite(db:Session,user_id:int,product_id:int):
    favorite=is_favorite(db,user_id,product_id)
    if not favorite:
        raise HTTPException(status_code=404,detail='Not found')
    return delete(db,favorite)


def statistics(db:Session):
    products=db.query(models.Product).all()
    orders=db.query(models.Order).filter(models.Order.status!='cancelled').all()

    expensive=None
    cheap=None
    max_price=0
    min_price=0
    low_stock=[]
    for product in products:
        if expensive is None or product.price>max_price:
            max_price=product.price
            expensive=product.name
        if cheap is None or product.price<min_price:
            min_price=product.price
            cheap=product.name
        if product.stock<5:
            low_stock.append(product.name)

    total=0
    sold={}
    spent={}
    for order in orders:
        total+=order.total
        if order.user_id not in spent:
            spent[order.user_id]=0
        spent[order.user_id]+=order.total
        for item in order.items:
            if item.product.name not in sold:
                sold[item.product.name]=0
            sold[item.product.name]+=item.quantity

    best_product=None
    for name in sold:
        if best_product is None or sold[name]>sold[best_product]:
            best_product=name

    top_user=None
    for user_id in spent:
        if top_user is None or spent[user_id]>spent[top_user]:
            top_user=user_id

    average=0
    if orders:
        average=total/len(orders)

    return {
        'users_count':db.query(models.User).count(),
        'products_count':len(products),
        'categories_count':db.query(models.Category).count(),
        'orders_count':len(orders),
        'total_sum':total,
        'average_order':average,
        'best_selling_product':best_product,
        'most_expensive_product':expensive,
        'cheapest_product':cheap,
        'low_stock_products':low_stock,
        'top_user_id':top_user
    }
