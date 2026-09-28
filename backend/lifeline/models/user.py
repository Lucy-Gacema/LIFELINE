import enum
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid


class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    CASHIER = "Cashier"


DEFAULT_ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        "edit_price", "apply_discount", "refund_sale", "adjust_inventory",
        "view_profit", "edit_products", "manage_users", "access_reports",
        "change_settings", "manage_suppliers", "manage_customers",
        "void_transaction", "manage_expenses", "manage_shifts",
    },
    UserRole.MANAGER: {
        "edit_price", "apply_discount", "refund_sale", "adjust_inventory",
        "view_profit", "edit_products", "access_reports",
        "manage_suppliers", "manage_customers", "manage_expenses",
        "manage_shifts",
    },
    UserRole.CASHIER: {
        "manage_shifts", 
    },
}


class User(Base):
    __tablename__ = "users"

    user_id = Column(GUID(), primary_key=True, default=new_uuid)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)  
    pin = Column(String, nullable=True) 
    role = Column(String, nullable=False, default=UserRole.CASHIER.value)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    custom_permissions = Column(JSON, nullable=True)  
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    last_login_at = Column(DateTime, nullable=True)

    def effective_permissions(self) -> set:
        base = set(DEFAULT_ROLE_PERMISSIONS.get(UserRole(self.role), set()))
        if self.custom_permissions:
            for perm, allowed in self.custom_permissions.items():
                if allowed:
                    base.add(perm)
                else:
                    base.discard(perm)
        return base

    def has_permission(self, permission: str) -> bool:
        return permission in self.effective_permissions()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
