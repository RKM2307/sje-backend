from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EnquiryCreate(BaseModel):
    customer_name: str
    phone: str
    email: Optional[EmailStr] = None
    enquiry_type: Optional[str] = "Product Enquiry"
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    pump_brand: Optional[str] = None
    pump_model: Optional[str] = None
    quantity: int = 1
    message: Optional[str] = None
    image_url: Optional[str] = None
    preferred_contact: Optional[str] = "WhatsApp"

class EnquiryUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None

class EnquiryOut(EnquiryCreate):
    id: int
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    product_name: Optional[str] = None
    variant_name: Optional[str] = None

    class Config:
        from_attributes = True

class ServiceRequestCreate(BaseModel):
    customer_name: str
    phone: str
    email: Optional[EmailStr] = None
    pump_brand: Optional[str] = None
    pump_model: Optional[str] = None
    service_type: str
    problem_description: str
    image_url: Optional[str] = None
    preferred_contact: Optional[str] = "WhatsApp"

class ServiceRequestUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None

class ServiceRequestOut(ServiceRequestCreate):
    id: int
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
