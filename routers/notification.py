from fastapi import APIRouter , Request , Depends
from fastapi.templating import Jinja2Templates
from database import get_db
from sqlalchemy.orm import Session
from auth import get_current_user
import models


router = APIRouter(prefix="/notification" , tags=["Notification"])
templates = Jinja2Templates(directory="templates")

@router.get("/all")
def index(request:Request):
    return templates.TemplateResponse(request=request,name="notification.html")

@router.get("/get_all")
def index(db : Session = Depends(get_db) , current_user = Depends(get_current_user)):
    
    notifications = db.query(models.Notification).filter(models.Notification.user_id == current_user.id).order_by(models.Notification.created_at.desc()).all()
    return notifications 

@router.get("/one/{id}")
def index(id : int , db : Session = Depends(get_db) , current_user = Depends(get_current_user)):
    notification = db.query(models.Notification).filter(models.Notification.id == id , models.Notification.user_id == current_user.id).first()
    return notification

@router.delete("/delete/{id}")
def index(id : int , db : Session = Depends(get_db) , current_user = Depends(get_current_user)):
    notification = db.query(models.Notification).filter(models.Notification.id == id , models.Notification.user_id == current_user.id)
    notification.delete(synchronize_session=False)
    db.commit()
    return {"message" : "Notification deleted"}