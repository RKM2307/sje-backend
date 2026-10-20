import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    email = Column(String(120), nullable=True)
    enquiry_type = Column(String(80), default="Product Enquiry")  # Product Enquiry, Spare Part Identification, Bulk Order, Price Check
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    pump_brand = Column(String(100), nullable=True)
    pump_model = Column(String(100), nullable=True)
    quantity = Column(Integer, default=1)
    message = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)  # Photo upload for part identification
    preferred_contact = Column(String(50), default="WhatsApp")  # WhatsApp, Phone, Email
    status = Column(String(50), default="New", index=True)  # New, In Progress, Quoted, Closed
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("Product", back_populates="enquiries")
    variant = relationship("ProductVariant", back_populates="enquiries")

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    email = Column(String(120), nullable=True)
    pump_brand = Column(String(100), nullable=True)
    pump_model = Column(String(100), nullable=True)
    service_type = Column(String(100), nullable=False)  # Pump Inspection, Motor Service, Repair Enquiry, Spare-Part Replacement, Maintenance
    problem_description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    preferred_contact = Column(String(50), default="WhatsApp")  # WhatsApp, Phone
    status = Column(String(50), default="New", index=True)  # New, Contacted, In Progress, Completed, Cancelled
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
