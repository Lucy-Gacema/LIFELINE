from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.schemas.users import UserCreate, UserUpdate, UserOut
from lifeline.core.security import hash_secret
from lifeline.services import audit_service

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def _to_out(user: User) -> UserOut:
    return UserOut(
        user_id=user.user_id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role, is_active=user.is_active,
        permissions=sorted(user.effective_permissions()),
    )


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return [_to_out(u) for u in db.query(User).all()]


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A user with that email already exists.")
    user = User(
        email=data.email, first_name=data.first_name, last_name=data.last_name,
        role=data.role.value, password=hash_secret(data.password),
        pin=hash_secret(data.pin) if data.pin else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    audit_service.log_action(db, current_user.user_id, "user.created", "user", user.user_id, new_value={"email": user.email})
    return _to_out(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: str, data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    update_data = data.model_dump(exclude_unset=True)
    if "role" in update_data and update_data["role"] is not None:
        update_data["role"] = update_data["role"].value
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    audit_service.log_action(db, current_user.user_id, "user.updated", "user", user.user_id, new_value=update_data)
    return _to_out(user)
