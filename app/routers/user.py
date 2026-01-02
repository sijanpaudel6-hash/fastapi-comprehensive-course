from fastapi import status, HTTPException, APIRouter, Depends
from sqlmodel import Session, select
from ..database import engine, get_session
from .. import models, utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=models.UserPublic)
def create_user(user: models.UserCreate, session: Session = Depends(get_session)):
    
    email = session.exec(select(models.User).where(models.User.email == user.email)).first()
    if email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")
    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=models.UserPublicWithPosts)
def get_user(id: int, session: Session = Depends(get_session)):
    user = session.get(models.User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"user with id: {id} was not found")
    return user