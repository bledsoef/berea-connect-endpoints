from fastapi import FastAPI, HTTPException, Depends, status
from mangum import Mangum
import models
from typing import Annotated
from pydantic import BaseModel
from database import engine, SessionLocal
from sqlalchemy.orm import Session
app = FastAPI()
models.Base.metadata.create_all(bind=engine)
handler = Mangum(app)

class UserBase(BaseModel):
    username: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def home():
    return {"message": "you have reached the home page"}

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id:int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user