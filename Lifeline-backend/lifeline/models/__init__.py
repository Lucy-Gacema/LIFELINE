from database import Base, engine
from lifeline.models.credits import Credit
from lifeline.models.sales import Sale
from lifeline.models.products import Product
from lifeline.models.inventory_logs import InventoryLogs

__all__ =[
    "Credit",
    "Sale",
    "Product",
    "InventoryLogs",
    "Users"
]

def create_tables():
    Base.metadata.create_all(bind=engine)

