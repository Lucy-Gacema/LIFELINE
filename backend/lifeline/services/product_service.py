import uuid
from typing import List, Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from lifeline.models.product import Product
from lifeline.schemas.products import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump(exclude_unset=True))
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id) -> Optional[Product]:
    return db.query(Product).filter(Product.product_id == product_id).first()


def list_products(
    db: Session,
    search: Optional[str] = None,
    category_id: Optional[uuid.UUID] = None,
    active_only: bool = True,
    favorites_only: bool = False,
    limit: int = 200,
) -> List[Product]:
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)  # noqa: E712
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if favorites_only:
        query = query.filter(Product.is_favorite == True)  # noqa: E712
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Product.product_name).like(like),
                func.lower(Product.sku).like(like),
                func.lower(Product.barcode).like(like),
            )
        )
    return query.order_by(Product.product_name).limit(limit).all()


def find_product_by_lookup(db: Session, term: str) -> List[Product]:
   
    term_norm = term.strip().lower()
    if not term_norm:
        return []

    candidates = (
        db.query(Product)
        .filter(Product.is_active == True)  # noqa: E712
        .all()
    )

    matches = []
    for p in candidates:
        haystacks = [p.product_name.lower()]
        if p.sku:
            haystacks.append(p.sku.lower())
        if p.barcode:
            haystacks.append(p.barcode.lower())
        if p.aliases:
            haystacks.extend([a.lower() for a in p.aliases])

        if any(term_norm == h or term_norm in h or h in term_norm for h in haystacks):
            matches.append(p)

    
    matches.sort(key=lambda p: 0 if term_norm == p.product_name.lower() else 1)
    return matches


def get_low_stock_products(db: Session, threshold_override: Optional[int] = None) -> List[Product]:
    products = db.query(Product).filter(Product.is_active == True).all()  # noqa: E712
    threshold = threshold_override
    result = []
    for p in products:
        limit = threshold if threshold is not None else p.minimum_stock
        if p.current_stock <= limit:
            result.append(p)
    return result
