import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from lifeline.models.audit_log import AuditLog


def _json_safe(value):

    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def log_action(
    db: Session,
    user_id,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    previous_value: dict | None = None,
    new_value: dict | None = None,
    reason: str | None = None,
    commit: bool = True,
):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        previous_value=_json_safe(previous_value),
        new_value=_json_safe(new_value),
        reason=reason,
    )
    db.add(entry)
    if commit:
        db.commit()
    return entry
