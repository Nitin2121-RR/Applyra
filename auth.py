from fastapi.security import OAuth2PasswordBearer
from jose import JWTError , jwt 
from datetime import datetime , timedelta
from dotenv import load_dotenv
import os
from fastapi import Depends , HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

oauth = OAuth2PasswordBearer("/user/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
def create_access_token(data : dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token : str , credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id : str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_id = {"id": id}
    except JWTError:
        raise credentials_exception
    
    return token_id
def get_current_user(token : str = Depends(oauth) , db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    id = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == id['id']).first()
    return user 

