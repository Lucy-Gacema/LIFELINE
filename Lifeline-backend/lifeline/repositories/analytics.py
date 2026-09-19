from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from lifeline.models.sales import Sale
from lifeline.models.products import Product
from lifeline.models.credits import Credit

class AnalyticsRepository:
    
    def get_money_tied_in_debts(self, db: Session) -> Decimal:
        result = db.query(
            func.coalesce(func.sum(Credit.amount_owed), 0)
        ).filter(Credit.is_paid == False).scalar()
        return Decimal(str(result))

    def get_total_profit(self, db: Session) -> Decimal:
        result = db.query(
            func.coalesce(
                func.sum(Sale.quantity_sold * (Product.selling_price - Product.buying_price)), 
                0
            )
        ).join(Product, Sale.product_id == Product.product_id).scalar()
        return Decimal(str(result))

    def get_total_revenue(self, db: Session) -> Decimal:
        result = db.query(
            func.coalesce(
                func.sum(Sale.quantity_sold * Product.selling_price), 
                0
            )
        ).join(Product, Sale.product_id == Product.product_id).scalar()
        return Decimal(str(result))

analytics_repository = AnalyticsRepository()
