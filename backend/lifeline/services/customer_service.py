from typing import List, Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from lifeline.models.customer import Customer
from lifeline.schemas.customers import CustomerCreate, CustomerUpdate


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, data: CustomerUpdate) -> Customer:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def search_customers(db: Session, term: str, limit: int = 20) -> List[Customer]:
    like = f"%{term.lower()}%"
    return (
        db.query(Customer)
        .filter(or_(func.lower(Customer.name).like(like), Customer.phone.like(f"%{term}%")))
        .limit(limit)
        .all()
    )
