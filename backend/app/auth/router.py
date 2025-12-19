from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, schemas
from . import jwt

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.login).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = jwt.get_password_hash(user.password)
    new_user = models.User(username=user.login, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"msg": "User created successfully"}

@router.post("/login", response_model=schemas.Token)
def login(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    db_user = db.query(models.User).filter(models.User.username == user.login).first()
    
    if not db_user or not jwt.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = jwt.create_access_token(data={
        "sub": str(db_user.id),
        "login": db_user.username,
        "is_admin": db_user.is_admin
    })
    return {"access_token": access_token, "token_type": "bearer"}
