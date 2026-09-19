from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from lifeline.repositories.users import user_repository
from lifeline.schemas.users import UserCreate, UserLoginRequest, TokenResponse
from lifeline.services.security import pwd_context
from lifeline.services.security import pwd_context, encrypt_password, verify_password, create_access_token

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = user_repository

    def encrypt_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def register_user(self, user_input: UserCreate):
        existing_user = self.repository.get_user_by_email(self.db, user_input.email)
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failure: An account with this email address already exists."
            )
        
        user_data = user_input.model_dump()
        
        if not user_data.get("role"):
            user_data["role"] = "user"
            
        user_data["password"] = self.encrypt_password(user_input.password)
        new_user = self.repository.create(self.db, user_data)
        return new_user

    def authenticate_user(self, login_data: UserLoginRequest) -> TokenResponse:
        user = self.repository.get_user_by_email(self.db, login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Invalid login credentials provided."
            )
            
        if not self.verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Invalid login credentials provided."
            )
            
        token_claims = {
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role
        }
        
        access_token = create_access_token(data=token_claims)
        return TokenResponse(
            access_token=access_token,
            user_id=user.user_id,
            role=user.role
        )
    def get_user(self, user_id: UUID):
        user = self.repository.get(self.db, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        return user

    def get_all_users(self):
        return self.repository.get_all(self.db)

    def update_user(self, user_id: UUID, update_data: dict):
        db_obj = self.get_user(user_id)

        if "password" in update_data and update_data["password"]:
            update_data["password"] = pwd_context.hash(update_data["password"])

        return self.repository.update(self.db, update_data, db_obj)




    def delete_user(self, user_id: UUID):
        db_obj = self.get_user(user_id)
        self.repository.delete(self.db, db_obj)


