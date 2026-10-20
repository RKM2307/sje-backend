from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Brand, Product
from app.models.user import AdminUser
from app.schemas.product import BrandOut, BrandCreate
from app.services.auth import get_current_admin_user

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("", response_model=List[BrandOut])
def list_brands(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Brand)
    if active_only:
        q = q.filter(Brand.active == True)
    brands = q.all()

    result = []
    for b in brands:
        p_count = db.query(func.count(Product.id)).filter(Product.brand_id == b.id, Product.published == True).scalar() or 0
        b_dict = {
            "id": b.id,
            "name": b.name,
            "slug": b.slug,
            "logo_url": b.logo_url,
            "authorisation_status": b.authorisation_status,
            "description": b.description,
            "active": b.active,
            "product_count": p_count
        }
        result.append(BrandOut(**b_dict))
    return result

@router.post("", response_model=BrandOut)
def create_brand(
    data: BrandCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    brand = Brand(**data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.put("/{brand_id}", response_model=BrandOut)
def update_brand(
    brand_id: int,
    data: BrandCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    for k, v in data.model_dump().items():
        setattr(brand, k, v)
    db.commit()
    db.refresh(brand)
    return brand
