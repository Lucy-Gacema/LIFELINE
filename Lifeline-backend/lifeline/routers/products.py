from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from lifeline.services.products import ProductService
from lifeline.schemas.products import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

def get_srv(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(p: ProductCreate, s: ProductService = Depends(get_srv)):
    return s.create_product(p.model_dump())

@router.get("/", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
def read_products(s: ProductService = Depends(get_srv)):
    return s.get_all_products()

@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def read_product(product_id: UUID, s: ProductService = Depends(get_srv)):
    return s.get_product(product_id)

@router.put("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(product_id: UUID, p: ProductUpdate, s: ProductService = Depends(get_srv)):
    return s.update_product(product_id, p.model_dump(exclude_unset=True))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, s: ProductService = Depends(get_srv)):
    s.delete_product(product_id)
    return None

@router.get("/{product_id}/name", response_model=str, status_code=status.HTTP_200_OK)
def read_product_name(product_id: UUID, s: ProductService = Depends(get_srv)):
    return s.get_product_name(product_id)

