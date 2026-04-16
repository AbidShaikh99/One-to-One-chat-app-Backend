from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas.user import UserCreate, LoginSchema
from app.config.settings import hash_password, verify_password, create_access_token
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=201)
def register(user : UserCreate, db : Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    
    if existing_user:
        return JSONResponse(
            status_code=400,
            content={
                "status": False,
                "message": "Email Already Exist.",
                "data": None
            }
        )
    db_user = models.User(
        name = user.name,
        email = user.email,
        password = hash_password(user.password),
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return{
        "status": True,
        "message": "User Registered Successfully.",
        "data":{
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
        }
    }

@router.post("/login")
def login(user : LoginSchema, db : Session = Depends(get_db)):
    
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    
    if not db_user or not verify_password(user.password, db_user.password):
        return JSONResponse(
            status_code=400,
            content={
                "status": False,
                "message": "Invalid Credentials",
                "data": None
            }
        )
    
    token = create_access_token({
        "user_id": db_user.id,
    })
    return JSONResponse(
        content={
            "status": True,
            "message": "Login Successfully.",
            "access_token": token,
            "token_type": "bearer"
        }
    )