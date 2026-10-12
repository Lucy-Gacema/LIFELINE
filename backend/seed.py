import os
import sys
from decimal import Decimal

from database import sessionLocal
from lifeline.core.security import hash_secret
from lifeline.models import create_tables
from lifeline.models.user import User, UserRole


def main():
    create_tables()
    db = sessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Users already exist — skipping seed.")
            return

        admin_email = os.environ.get("SEED_ADMIN_EMAIL")
        admin_password = os.environ.get("SEED_ADMIN_PASSWORD")
        admin_pin = os.environ.get("SEED_ADMIN_PIN")

        if not admin_email or not admin_password or not admin_pin:
            sys.exit(
                "Set SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD and SEED_ADMIN_PIN "
                "as environment variables before running this script."
            )
        if len(admin_password) < 8:
            sys.exit("SEED_ADMIN_PASSWORD must be at least 8 characters.")

        admin = User(
            email=admin_email,
            password=hash_secret(admin_password),
            pin=hash_secret(admin_pin),
            role=UserRole.ADMIN.value,
            first_name="Shop",
            last_name="Owner",
        )
        db.add(admin)
        db.commit()
        print(f"Admin account created: {admin_email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()