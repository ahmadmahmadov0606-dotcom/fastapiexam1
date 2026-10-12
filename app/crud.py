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

def change_status(db:Session,order_id:int,data:schemas.OrderStatus):
    order=get_or_404(db,models.Order,order_id)
    if data.status not in ['new','paid','cancelled']:
        raise HTTPException(status_code=400,detail='Wrong status')
    if order.status=='cancelled':
        raise HTTPException(status_code=400,detail='Order is cancelled')
    if data.status=='cancelled':
        for item in order.items:
            item.product.stock+=item.quantity
    order.status=data.status
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
    if db.query(models.Favorite).filter_by(user_id=data.user_id,product_id=data.product_id).first():
        raise HTTPException(status_code=400,detail='Already in favorites')
    return create(db,models.Favorite(**data.model_dump()))


def statistics(db:Session):
    products=db.query(models.Product).all()
    orders=db.query(models.Order).filter(models.Order.status!='cancelled').all()
    total=0
    sold={}
    spent={}
    for order in orders:
        total+=order.total
        spent[order.user_id]=spent.get(order.user_id,0)+order.total
        for item in order.items:
            sold[item.product.name]=sold.get(item.product.name,0)+item.quantity
    low_stock=[]
    for product in products:
        if product.stock<5:
            low_stock.append(product.name)
    return {
        'users_count':db.query(models.User).count(),
        'products_count':len(products),
        'categories_count':db.query(models.Category).count(),
        'orders_count':len(orders),
        'total_sum':total,
        'average_order':total/len(orders) if orders else 0,
        'best_selling_product':max(sold,key=sold.get) if sold else None,
        'most_expensive_product':max(products,key=lambda p:p.price).name if products else None,
        'cheapest_product':min(products,key=lambda p:p.price).name if products else None,
        'low_stock_products':low_stock,
        'top_user_id':max(spent,key=spent.get) if spent else None
    }
