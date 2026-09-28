import enum


class ReasonEnum(str, enum.Enum):
    SALE = "sale"
    RESTOCK = "restock"
    DAMAGE = "damage"
    WRITE_OFF = "write_off"
    CORRECTION = "correction"
    RETURN = "return"
    TRANSFER = "transfer"
    INITIAL_STOCK = "initial_stock"
