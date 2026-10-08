import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.customer import Customer
from lifeline.models.user import User
from lifeline.schemas.customers import CustomerCreate, CustomerOut, CustomerUpdate
from lifeline.services import customer_service

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get("/", response_model=list[CustomerOut])
def list_customers(
    search: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if search:
        return customer_service.search_customers(db, search)
    return db.query(Customer).order_by(Customer.name).limit(200).all()


@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return customer_service.create_customer(db, data)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found.")
    return customer


@router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_customers")),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found.")
    return customer_service.update_customer(db, customer, data)
