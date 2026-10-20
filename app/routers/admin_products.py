import re
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import AdminUser
from app.models.product import Product, ProductVariant, Brand, Category, PumpModel, ProductCompatibility
from app.models.enquiry import Enquiry, ServiceRequest
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductDetailOut, ProductListItem,
    ProductVariantCreate, ProductVariantUpdate, ProductVariantOut,
    CompatibilityCreate, CompatibilityOut
)
from app.services.auth import get_current_admin_user
from app.services.csv_service import generate_csv_template, process_csv_import

router = APIRouter(prefix="/admin", tags=["Admin Products & Inventory"])

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    total_products = db.query(Product).count()
    published_products = db.query(Product).filter(Product.published == True).count()
    draft_products = db.query(Product).filter(Product.published == False).count()
    total_variants = db.query(ProductVariant).count()
    low_stock_variants = db.query(ProductVariant).filter(ProductVariant.quantity <= 3).count()
    pending_enquiries = db.query(Enquiry).filter(Enquiry.status.in_(["New", "In Progress"])).count()
    pending_services = db.query(ServiceRequest).filter(ServiceRequest.status.in_(["New", "Contacted", "In Progress"])).count()

    categories_stats = db.query(
        Category.name,
        func.count(Product.id)
    ).outerjoin(Product, Category.id == Product.category_id).group_by(Category.name).all()

    return {
        "total_products": total_products,
        "published_products": published_products,
        "draft_products": draft_products,
        "total_variants": total_variants,
        "low_stock_variants": low_stock_variants,
        "pending_enquiries": pending_enquiries,
        "pending_services": pending_services,
        "categories_stats": [{"category": name, "count": count} for name, count in categories_stats]
    }

@router.get("/products")
def list_admin_products(
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    brand_id: Optional[int] = Query(None),
    published: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    query = db.query(Product)
    if published is not None:
        query = query.filter(Product.published == published)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            (Product.name.ilike(term)) |
            (Product.reference_number.cast(Product.name.type).ilike(term)) |
            (Product.manufacturer_part_number.ilike(term))
        )

    total = query.count()
    products = query.order_by(Product.reference_number.asc()).offset((page - 1) * limit).limit(limit).all()

    items = []
    for p in products:
        items.append({
            "id": p.id,
            "reference_number": p.reference_number,
            "name": p.name,
            "slug": p.slug,
            "brand_id": p.brand_id,
            "brand_name": p.brand.name if p.brand else None,
            "category_id": p.category_id,
            "category_name": p.category.name if p.category else None,
            "manufacturer_part_number": p.manufacturer_part_number,
            "published": p.published,
            "featured": p.featured,
            "stock_status": p.stock_status,
            "primary_image_url": p.primary_image_url,
            "variants_count": len(p.variants),
            "updated_at": p.updated_at
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 1
    }

@router.post("/products", response_model=ProductDetailOut)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    # Rule 3: Duplicate reference IDs are strictly prevented!
    existing_ref = db.query(Product).filter(Product.reference_number == data.reference_number).first()
    if existing_ref:
        raise HTTPException(
            status_code=400,
            detail=f"Catalogue Reference ID #{data.reference_number} already exists for '{existing_ref.name}'. Duplicates are prevented."
        )

    slug_candidate = data.slug or slugify(f"{data.reference_number}-{data.name}")
    # Ensure unique slug
    base_slug = slug_candidate
    counter = 1
    while db.query(Product).filter(Product.slug == slug_candidate).first():
        slug_candidate = f"{base_slug}-{counter}"
        counter += 1

    new_prod = Product(
        reference_number=data.reference_number,
        name=data.name,
        slug=slug_candidate,
        description=data.description,
        brand_id=data.brand_id,
        category_id=data.category_id,
        model_number=data.model_number,
        manufacturer_part_number=data.manufacturer_part_number,
        specifications=data.specifications or {},
        primary_image_url=data.primary_image_url,
        published=data.published,
        featured=data.featured,
        stock_status=data.stock_status or "Contact for Availability",
        verification_notes=data.verification_notes,
        seo_title=data.seo_title or f"Part {data.reference_number} - {data.name} | Sri Jayavarman Electricals",
        seo_description=data.seo_description or f"Buy or enquire about Part {data.reference_number} ({data.name}) pump spare part in Thoothukudi (Tuticorin)."
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod

@router.get("/products/{product_id}", response_model=ProductDetailOut)
def get_admin_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    compat_list = [
        CompatibilityOut(
            id=c.id,
            product_id=c.product_id,
            variant_id=c.variant_id,
            pump_model_id=c.pump_model_id,
            model_name=c.pump_model.model_name if c.pump_model else None,
            brand_name=c.pump_model.brand.name if c.pump_model and c.pump_model.brand else None,
            pump_type=c.pump_model.pump_type if c.pump_model else None,
            compatibility_notes=c.compatibility_notes,
            verified=c.verified
        ) for c in prod.compatibilities
    ]

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
        variants=[ProductVariantOut.model_validate(v) for v in prod.variants],
        compatibilities=compat_list
    )

@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    # If updating reference_number, verify uniqueness
    if data.reference_number is not None and data.reference_number != prod.reference_number:
        existing = db.query(Product).filter(Product.reference_number == data.reference_number).first()
        if existing and existing.id != prod.id:
            raise HTTPException(
                status_code=400,
                detail=f"Catalogue Reference ID #{data.reference_number} is already in use by '{existing.name}'."
            )
        prod.reference_number = data.reference_number

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        if field != "reference_number":
            setattr(prod, field, val)

    db.commit()
    db.refresh(prod)
    return {"message": "Product updated successfully", "id": prod.id}

@router.post("/products/{product_id}/toggle-publish")
def toggle_publish(
    product_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    prod.published = not prod.published
    db.commit()
    return {"id": prod.id, "published": prod.published}

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    ref_num = prod.reference_number
    db.delete(prod)
    db.commit()
    return {"message": f"Product Ref #{ref_num} deleted successfully"}

# Variant Management
@router.post("/products/{product_id}/variants", response_model=ProductVariantOut)
def add_product_variant(
    product_id: int,
    data: ProductVariantCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    variant = ProductVariant(
        product_id=product_id,
        variant_name=data.variant_name,
        sku=data.sku or f"SJE-{prod.reference_number:03d}-{len(prod.variants) + 1:02d}",
        dimensions=data.dimensions or {},
        material=data.material,
        compatible_models=data.compatible_models,
        price=data.price,
        quantity=data.quantity,
        stock_status=data.stock_status or "Contact for Price",
        image_url=data.image_url or prod.primary_image_url,
        active=data.active
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant

@router.put("/variants/{variant_id}", response_model=ProductVariantOut)
def update_product_variant(
    variant_id: int,
    data: ProductVariantUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(variant, field, val)

    db.commit()
    db.refresh(variant)
    return variant

@router.delete("/variants/{variant_id}")
def delete_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    db.delete(variant)
    db.commit()
    return {"message": "Variant deleted successfully"}

# Compatibility Management
@router.post("/products/{product_id}/compatibility")
def add_compatibility(
    product_id: int,
    data: CompatibilityCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    pump_model = db.query(PumpModel).filter(PumpModel.id == data.pump_model_id).first()
    if not pump_model:
        raise HTTPException(status_code=404, detail="Pump Model not found")

    compat = ProductCompatibility(
        product_id=product_id,
        variant_id=data.variant_id,
        pump_model_id=data.pump_model_id,
        compatibility_notes=data.compatibility_notes,
        verified=data.verified
    )
    db.add(compat)
    db.commit()
    db.refresh(compat)
    return {"message": "Compatibility added successfully", "id": compat.id}

@router.delete("/compatibility/{compat_id}")
def delete_compatibility(
    compat_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    compat = db.query(ProductCompatibility).filter(ProductCompatibility.id == compat_id).first()
    if not compat:
        raise HTTPException(status_code=404, detail="Compatibility link not found")
    db.delete(compat)
    db.commit()
    return {"message": "Compatibility removed successfully"}

# CSV Export and Import
@router.get("/export-csv")
def export_csv(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    csv_data = generate_csv_template(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sri_jayavarman_electricals_inventory_50_parts.csv"}
    )

@router.post("/import-csv")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")
    
    contents = await file.read()
    decoded = contents.decode("utf-8", errors="replace")
    updated, variants_added, errors = process_csv_import(decoded, db)

    return {
        "success": True,
        "products_updated": updated,
        "variants_created": variants_added,
        "errors": errors
    }
