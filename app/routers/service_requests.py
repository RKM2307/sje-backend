from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enquiry import ServiceRequest
from app.models.user import AdminUser
from app.schemas.enquiry import ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestOut
from app.services.auth import get_current_admin_user

router = APIRouter(prefix="/service-requests", tags=["Service Requests"])

@router.post("", response_model=ServiceRequestOut, status_code=status.HTTP_201_CREATED)
def submit_service_request(data: ServiceRequestCreate, db: Session = Depends(get_db)):
    if not data.customer_name or not data.phone or not data.problem_description:
        raise HTTPException(status_code=400, detail="Name, phone number and problem description are required.")

    req = ServiceRequest(
        customer_name=data.customer_name.strip(),
        phone=data.phone.strip(),
        email=data.email,
        pump_brand=data.pump_brand,
        pump_model=data.pump_model,
        service_type=data.service_type,
        problem_description=data.problem_description,
        image_url=data.image_url,
        preferred_contact=data.preferred_contact or "WhatsApp",
        status="New"
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.get("", response_model=List[ServiceRequestOut])
def list_service_requests(
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    q = db.query(ServiceRequest)
    if status_filter:
        q = q.filter(ServiceRequest.status == status_filter)
    return q.order_by(ServiceRequest.created_at.desc()).all()

@router.put("/{request_id}", response_model=ServiceRequestOut)
def update_service_request(
    request_id: int,
    data: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Service request not found")

    if data.status:
        req.status = data.status
    if data.admin_notes is not None:
        req.admin_notes = data.admin_notes

    db.commit()
    db.refresh(req)
    return req
