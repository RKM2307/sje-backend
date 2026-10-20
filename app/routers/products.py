from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.product import Product, ProductVariant, Brand, Category, ProductCompatibility, PumpModel
from app.schemas.product import (
    ProductListItem, ProductDetailOut, PaginatedProducts, ProductVariantOut, CompatibilityOut
)
from app.services.search_service import search_products

router = APIRouter(prefix="/products", tags=["Products (Public)"])

def map_product_to_list_item(prod: Product) -> ProductListItem:
    prices = [v.price for v in prod.variants if v.price is not None and v.active]
    min_price = min(prices) if prices else None
    return ProductListItem(
        id=prod.id,
        reference_number=prod.reference_number,
        name=prod.name,
        slug=prod.slug,
        description=prod.description,
        brand_name=prod.brand.name if prod.brand else None,
        brand_id=prod.brand_id,
        category_name=prod.category.name if prod.category else None,
        category_id=prod.category_id,
        primary_image_url=prod.primary_image_url,
        published=prod.published,
        featured=prod.featured,
        stock_status=prod.stock_status,
        variant_count=len(prod.variants),
        starting_price=min_price,
        created_at=prod.created_at,
        updated_at=prod.updated_at
    )

@router.get("", response_model=PaginatedProducts)
def list_products(
    q: Optional[str] = Query(None, description="Search by name, ref #, dimension, brand, model"),
    category_id: Optional[int] = Query(None),
    brand_id: Optional[int] = Query(None),
    stock_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    products, total = search_products(
        db=db,
        query=q,
        category_id=category_id,
        brand_id=brand_id,
        stock_status=stock_status,
        published_only=True,
        limit=limit,
        offset=offset
    )

    items = [map_product_to_list_item(p) for p in products]
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return PaginatedProducts(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.get("/featured", response_model=List[ProductListItem])
def get_featured_products(limit: int = Query(8, ge=1, le=20), db: Session = Depends(get_db)):
    products = db.query(Product).filter(
        Product.published == True,
        Product.featured == True
    ).order_by(Product.reference_number.asc()).limit(limit).all()

    # If fewer featured than limit, backfill with published products
    if len(products) < limit:
        existing_ids = [p.id for p in products]
        fill = db.query(Product).filter(
            Product.published == True,
            Product.id.notin_(existing_ids)
        ).order_by(Product.reference_number.asc()).limit(limit - len(products)).all()
        products.extend(fill)

    return [map_product_to_list_item(p) for p in products]

@router.get("/ref/{ref_number}", response_model=ProductDetailOut)
def get_product_by_ref_number(ref_number: int, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.reference_number == ref_number).first()
    if not prod:
        raise HTTPException(status_code=404, detail=f"No product found for Catalogue Reference #{ref_number}")
    return format_product_detail(prod, db)

@router.get("/{identifier}", response_model=ProductDetailOut)
def get_product_detail(identifier: str, db: Session = Depends(get_db)):
    # Match by ID or Slug
    prod = None
    if identifier.isdigit():
        prod = db.query(Product).filter(Product.id == int(identifier)).first()
    if not prod:
        prod = db.query(Product).filter(Product.slug == identifier).first()

    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    return format_product_detail(prod, db)

def format_product_detail(prod: Product, db: Session) -> ProductDetailOut:
    compat_list = []
    for c in prod.compatibilities:
        compat_list.append(CompatibilityOut(
            id=c.id,
            product_id=c.product_id,
            variant_id=c.variant_id,
            pump_model_id=c.pump_model_id,
            model_name=c.pump_model.model_name if c.pump_model else None,
            brand_name=c.pump_model.brand.name if c.pump_model and c.pump_model.brand else None,
            pump_type=c.pump_model.pump_type if c.pump_model else None,
            compatibility_notes=c.compatibility_notes,
            verified=c.verified
        ))

    return ProductDetailOut(
        id=prod.id,
        reference_number=prod.reference_number,
        name=prod.name,
        slug=prod.slug,
        description=prod.description,
        brand_id=prod.brand_id,
        category_id=prod.category_id,
        model_number=prod.model_number,
        manufacturer_part_number=prod.manufacturer_part_number,
        specifications=prod.specifications or {},
        primary_image_url=prod.primary_image_url,
        published=prod.published,
        featured=prod.featured,
        stock_status=prod.stock_status,
        verification_notes=prod.verification_notes,
        seo_title=prod.seo_title,
        seo_description=prod.seo_description,
        created_at=prod.created_at,
        updated_at=prod.updated_at,
        brand=prod.brand,
        category=prod.category,
        variants=[ProductVariantOut.model_validate(v) for v in prod.variants if v.active],
        compatibilities=compat_list
    )

@router.get("/{identifier}/related", response_model=List[ProductListItem])
def get_related_products(identifier: str, limit: int = Query(4, ge=1, le=10), db: Session = Depends(get_db)):
    prod = None
    if identifier.isdigit():
        prod = db.query(Product).filter(Product.id == int(identifier)).first()
    if not prod:
        prod = db.query(Product).filter(Product.slug == identifier).first()

    if not prod or not prod.category_id:
        return []

    related = db.query(Product).filter(
        Product.category_id == prod.category_id,
        Product.id != prod.id,
        Product.published == True
    ).limit(limit).all()

    return [map_product_to_list_item(p) for p in related]
