import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.category import Category
from lifeline.models.user import User
from lifeline.schemas.products import (
    CategoryCreate,
    CategoryOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
)
from lifeline.services import audit_service, product_service

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("/", response_model=list[ProductOut])
def list_products(
    search: str | None = None,
    category_id: uuid.UUID | None = None,
    favorites_only: bool = False,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = product_service.list_products(
        db,
        search=search,
        category_id=category_id,
        active_only=not include_inactive,
        favorites_only=favorites_only,
    )
    return products


@router.get("/search", response_model=list[ProductOut])
def search_products(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Powers the fast Sell-screen search box: matches name, SKU, barcode, or alias."""
    return product_service.find_product_by_lookup(db, q)


@router.get("/low-stock", response_model=list[ProductOut])
def low_stock(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return product_service.get_low_stock_products(db)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_products")),
):
    product = product_service.create_product(db, data)
    audit_service.log_action(
        db,
        current_user.user_id,
        "product.created",
        "product",
        product.product_id,
        new_value={"name": product.product_name},
    )
    return product


@router.get("/categories/", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Category).all()


@router.post(
    "/categories/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_products")),
):
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found.")
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_products")),
):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found.")
    previous = {"selling_price": float(product.selling_price)}
    updated = product_service.update_product(db, product, data)
    audit_service.log_action(
        db,
        current_user.user_id,
        "product.updated",
        "product",
        product.product_id,
        previous_value=previous,
        new_value=data.model_dump(exclude_unset=True),
    )
    return updated


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_products")),
):
    """Soft-delete only — historical sales must keep referring to this product."""
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found.")
    product.is_active = False
    db.commit()
