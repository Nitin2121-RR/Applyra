from fastapi import APIRouter , Depends , Request , HTTPException
from fastapi.templating import Jinja2Templates
from database import get_db
import models
from sqlalchemy.orm import Session 
from schema import UserCreate , login_user
from passlib.context import CryptContext
from auth import create_access_token , get_current_user
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

template = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/user")

@router.get("/login")
def index(request : Request) :
    return template.TemplateResponse(
        request=request,
        name="login.html"
    )

@router.get("/register")
def index(request : Request) :
    return template.TemplateResponse(
        request=request,
        name="register.html"
    )

@router.post("/register")
def index(user : UserCreate , db : Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password) 
    new_user = models.User(username=user.username , email=user.email , password=hashed_password)
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=404 , detail="Email Already Exists")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success" : "Account Created"}

@router.post("/login")
def index(userss : login_user , db : Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == userss.email).first()
    if not user:
        raise HTTPException(status_code=404 , detail="User Not Found")
    if not pwd_context.verify(userss.password , user.password):
        raise HTTPException(status_code=404 , detail="Incorrect Password")
    
    token = create_access_token(data={"id": user.id})

    return {"access_token" : token , "token_type" : "bearer"}

@router.get("/dashboard")
def index(request : Request): 
    return template.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

@router.get("/me")
def index(current_user = Depends(get_current_user)):
    name = current_user.username
    return {"name" : name} 