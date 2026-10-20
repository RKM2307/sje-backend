from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Category, Product
from app.models.user import AdminUser
from app.schemas.product import CategoryOut, CategoryCreate
from app.services.auth import get_current_admin_user

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryOut])
def list_categories(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Category)
    if active_only:
        q = q.filter(Category.active == True)
    categories = q.order_by(Category.id.asc()).all()

    result = []
    for c in categories:
        p_count = db.query(func.count(Product.id)).filter(Product.category_id == c.id, Product.published == True).scalar() or 0
        c_dict = {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "parent_category_id": c.parent_category_id,
            "description": c.description,
            "image_url": c.image_url,
            "active": c.active,
            "product_count": p_count
        }
        result.append(CategoryOut(**c_dict))
    return result

@router.post("", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for k, v in data.model_dump().items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat
