
import sys
from decimal import Decimal

from database import sessionLocal, Base, engine
from lifeline.models import create_tables
from lifeline.models.user import User, UserRole
from lifeline.models.product import Product
from lifeline.models.category import Category
from lifeline.core.security import hash_secret


def main():
    create_tables()
    db = sessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Users already exist — skipping seed. Delete lifeline.db to start fresh.")
            return

        admin_email = input("Admin email [admin@myshop.com]: ").strip() or "admin@myshop.com"
        admin_password = input("Admin password [admin123]: ").strip() or "admin123"
        admin_pin = input("Admin PIN (4-6 digits) [1234]: ").strip() or "1234"

        admin = User(
            email=admin_email,
            password=hash_secret(admin_password),
            pin=hash_secret(admin_pin),
            role=UserRole.ADMIN.value,
            first_name="Shop",
            last_name="Owner",
        )
        db.add(admin)

        general = Category(name="General", icon="🛒")
        drinks = Category(name="Drinks", icon="🥤")
        db.add_all([general, drinks])
        db.flush()

        sample_products = [
            Product(product_name="Unga (2kg)", selling_price=Decimal("240"), buying_price=Decimal("200"), current_stock=30, minimum_stock=5, unit="packet", category_id=general.category_id, aliases=["unga", "flour", "maize flour"], is_favorite=True),
            Product(product_name="Milk 500ml", selling_price=Decimal("60"), buying_price=Decimal("50"), current_stock=40, minimum_stock=10, unit="packet", category_id=drinks.category_id, aliases=["milk", "maziwa"], is_favorite=True),
            Product(product_name="Milk 1L", selling_price=Decimal("110"), buying_price=Decimal("95"), current_stock=20, minimum_stock=5, unit="packet", category_id=drinks.category_id, aliases=["milk 1 litre", "big milk"]),
            Product(product_name="Bread", selling_price=Decimal("65"), buying_price=Decimal("55"), current_stock=25, minimum_stock=5, unit="loaf", category_id=general.category_id, aliases=["bread", "mkate"], is_favorite=True),
            Product(product_name="Sugar (1kg)", selling_price=Decimal("150"), buying_price=Decimal("130"), current_stock=15, minimum_stock=5, unit="packet", category_id=general.category_id, aliases=["sugar", "sukari"], is_favorite=True),
            Product(product_name="Soda 500ml", selling_price=Decimal("50"), buying_price=Decimal("40"), current_stock=48, minimum_stock=12, unit="bottle", category_id=drinks.category_id, aliases=["soda", "coke", "fanta"], is_favorite=True),
            Product(product_name="Water 500ml", selling_price=Decimal("40"), buying_price=Decimal("30"), current_stock=60, minimum_stock=12, unit="bottle", category_id=drinks.category_id, aliases=["water", "maji"], is_favorite=True),
            Product(product_name="Blue Band 250g", selling_price=Decimal("180"), buying_price=Decimal("150"), current_stock=12, minimum_stock=3, unit="tub", category_id=general.category_id, aliases=["blueband", "blue", "margarine"]),
        ]
        db.add_all(sample_products)
        db.commit()

        print(f"\nDone! Admin login: {admin_email} / {admin_password} (PIN: {admin_pin})")
        print("Sample products and categories were added so you can try a sale immediately.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
