from typing import Optional
from sqlalchemy.orm import Session
from lifeline.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    previous_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    reason: Optional[str] = None,
    commit: bool = True,
):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        previous_value=previous_value,
        new_value=new_value,
        reason=reason,
    )
    db.add(entry)
    if commit:
        db.commit()
    return entry
