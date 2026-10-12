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
