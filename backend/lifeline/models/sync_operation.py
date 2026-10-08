import enum

from sqlalchemy import JSON, Column, DateTime, Enum, String
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    CONFLICT = "conflict"


class SyncOperation(Base):
    __tablename__ = "sync_operations"

    sync_operation_id = Column(GUID(), primary_key=True, default=new_uuid)
    device_id = Column(String, nullable=False)
    idempotency_key = Column(String, nullable=False, unique=True, index=True)
    operation_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(
        Enum(SyncStatus, native_enum=False), nullable=False, default=SyncStatus.PENDING
    )
    error_message = Column(String, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    applied_at = Column(DateTime, nullable=True)
