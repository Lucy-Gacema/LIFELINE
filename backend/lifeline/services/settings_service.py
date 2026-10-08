from sqlalchemy.orm import Session

from lifeline.models.business_setting import BusinessSetting
from lifeline.schemas.settings import BusinessSettingsOut

_DEFAULTS = BusinessSettingsOut().model_dump()


def get_settings(db: Session) -> dict:
    rows = db.query(BusinessSetting).all()
    result = dict(_DEFAULTS)
    for row in rows:
        if row.key in result:
            result[row.key] = row.value
    return result


def update_settings(db: Session, updates: dict) -> dict:
    for key, value in updates.items():
        if value is None:
            continue
        row = db.query(BusinessSetting).filter(BusinessSetting.key == key).first()

        safe_value = float(value) if hasattr(value, "quantize") else value
        if row:
            row.value = safe_value
        else:
            db.add(BusinessSetting(key=key, value=safe_value))
    db.commit()
    return get_settings(db)
