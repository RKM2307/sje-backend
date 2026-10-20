from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enquiry import Enquiry
from app.models.product import Product, ProductVariant
from app.models.user import AdminUser
from app.schemas.enquiry import EnquiryCreate, EnquiryUpdate, EnquiryOut
from app.services.auth import get_current_admin_user

router = APIRouter(prefix="/enquiries", tags=["Enquiries"])

@router.post("", response_model=EnquiryOut, status_code=status.HTTP_201_CREATED)
def submit_enquiry(data: EnquiryCreate, db: Session = Depends(get_db)):
    if not data.customer_name or not data.phone:
        raise HTTPException(status_code=400, detail="Customer name and phone number are required.")

    # Validation: if product_id provided, ensure it exists
    if data.product_id:
        prod = db.query(Product).filter(Product.id == data.product_id).first()
        if not prod:
            raise HTTPException(status_code=400, detail="Selected product does not exist.")

    enquiry = Enquiry(
        customer_name=data.customer_name.strip(),
        phone=data.phone.strip(),
        email=data.email,
        enquiry_type=data.enquiry_type or "Product Enquiry",
        product_id=data.product_id,
        variant_id=data.variant_id,
        pump_brand=data.pump_brand,
        pump_model=data.pump_model,
        quantity=max(1, data.quantity),
        message=data.message,
        image_url=data.image_url,
        preferred_contact=data.preferred_contact or "WhatsApp",
        status="New"
    )
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)

    return EnquiryOut(
        id=enquiry.id,
        customer_name=enquiry.customer_name,
        phone=enquiry.phone,
        email=enquiry.email,
        enquiry_type=enquiry.enquiry_type,
        product_id=enquiry.product_id,
        variant_id=enquiry.variant_id,
        pump_brand=enquiry.pump_brand,
        pump_model=enquiry.pump_model,
        quantity=enquiry.quantity,
        message=enquiry.message,
        image_url=enquiry.image_url,
        preferred_contact=enquiry.preferred_contact,
        status=enquiry.status,
        admin_notes=enquiry.admin_notes,
        created_at=enquiry.created_at,
        product_name=enquiry.product.name if enquiry.product else None,
        variant_name=enquiry.variant.variant_name if enquiry.variant else None
    )

@router.get("", response_model=List[EnquiryOut])
def list_enquiries(
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    q = db.query(Enquiry)
    if status_filter:
        q = q.filter(Enquiry.status == status_filter)
    enquiries = q.order_by(Enquiry.created_at.desc()).all()

    result = []
    for e in enquiries:
        result.append(EnquiryOut(
            id=e.id,
            customer_name=e.customer_name,
            phone=e.phone,
            email=e.email,
            enquiry_type=e.enquiry_type,
            product_id=e.product_id,
            variant_id=e.variant_id,
            pump_brand=e.pump_brand,
            pump_model=e.pump_model,
            quantity=e.quantity,
            message=e.message,
            image_url=e.image_url,
            preferred_contact=e.preferred_contact,
            status=e.status,
            admin_notes=e.admin_notes,
            created_at=e.created_at,
            product_name=e.product.name if e.product else None,
            variant_name=e.variant.variant_name if e.variant else None
        ))
    return result

@router.put("/{enquiry_id}", response_model=EnquiryOut)
def update_enquiry(
    enquiry_id: int,
    data: EnquiryUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    e = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    if data.status:
        e.status = data.status
    if data.admin_notes is not None:
        e.admin_notes = data.admin_notes

    db.commit()
    db.refresh(e)

    return EnquiryOut(
        id=e.id,
        customer_name=e.customer_name,
        phone=e.phone,
        email=e.email,
        enquiry_type=e.enquiry_type,
        product_id=e.product_id,
        variant_id=e.variant_id,
        pump_brand=e.pump_brand,
        pump_model=e.pump_model,
        quantity=e.quantity,
        message=e.message,
        image_url=e.image_url,
        preferred_contact=e.preferred_contact,
        status=e.status,
        admin_notes=e.admin_notes,
        created_at=e.created_at,
        product_name=e.product.name if e.product else None,
        variant_name=e.variant.variant_name if e.variant else None
    )
