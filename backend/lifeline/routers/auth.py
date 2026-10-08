from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from lifeline.models.user import User
from lifeline.schemas.users import PinLoginRequest, Token, UserOut
from lifeline.services import security as sec_util

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        user_id=user.user_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        permissions=sorted(user.effective_permissions()),
    )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not sec_util.verify_secret(form_data.password, user.password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This account has been deactivated."
        )
    user.last_login_at = datetime.utcnow()
    db.commit()
    token = sec_util.create_access_token({"sub": str(user.user_id)})
    return Token(access_token=token, user=_to_user_out(user))


@router.post("/pin-login", response_model=Token)
def pin_login(data: PinLoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user or not user.pin or not sec_util.verify_secret(data.pin, user.pin):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect PIN.")
    if not user.is_active:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This account has been deactivated."
        )
    user.last_login_at = datetime.utcnow()
    db.commit()
    token = sec_util.create_access_token({"sub": str(user.user_id)})
    return Token(access_token=token, user=_to_user_out(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _to_user_out(current_user)


@router.get("/switch-user-list", response_model=list[UserOut])
def switch_user_list(db: Session = Depends(get_db)):

    users = db.query(User).filter(User.is_active == True).all()
    return [_to_user_out(u) for u in users]
