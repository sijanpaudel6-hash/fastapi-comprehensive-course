from fastapi import APIRouter, status, HTTPException, Response, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..schemas import UserLogin, Token
from ..database import get_session
from .. import models
from .. import utils, oauth2
from ..oauth2 import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(
        select(models.User).where(models.User.email == user_credentials.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    
    passwordValid = utils.verify_password(
        user_credentials.password, user.password
    )

    if not passwordValid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    
    # create token
    # return token

    access_token = oauth2.create_access_token(data={"user_id": user.id}, expires_time=ACCESS_TOKEN_EXPIRE_MINUTES)

    return {"access_token": access_token, "token_type": "bearer"}