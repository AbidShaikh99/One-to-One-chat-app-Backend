from pydantic import BaseModel,EmailStr
from typing import Optional, List
from datetime import datetime
class UserCreate(BaseModel):
    name: str
    email : EmailStr
    password : str

class LoginSchema(BaseModel):
    email : EmailStr
    password : str

class UserOut(BaseModel):
    id : int
    email : EmailStr
    
    class Config:
        from_attributes = True
class UserBasic(BaseModel):
    id: int
    name :str
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    sender_name: str
    receiver_name: str
    content: str
    timestamp: datetime