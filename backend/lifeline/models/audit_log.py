from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_log_id = Column(GUID(), primary_key=True, default=new_uuid)
    user_id = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=True)
    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(String, nullable=True)
    timestamp = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
