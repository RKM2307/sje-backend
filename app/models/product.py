import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, 
    ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    parent_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref="parent", remote_side=[id])

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    logo_url = Column(String(500), nullable=True)
    authorisation_status = Column(String(100), default="Authorisation Pending Verification")
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="brand")
    pump_models = relationship("PumpModel", back_populates="brand")

class PumpModel(Base):
    __tablename__ = "pump_models"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    model_name = Column(String(150), nullable=False)
    model_number = Column(String(100), index=True, nullable=True)
    pump_type = Column(String(100), nullable=True)  # Submersible, Monobloc, Openwell, Jet, etc.
    specifications = Column(JSON, default=dict)
    active = Column(Boolean, default=True)

    brand = relationship("Brand", back_populates="pump_models")
    compatibilities = relationship("ProductCompatibility", back_populates="pump_model")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(Integer, unique=True, index=True, nullable=False)  # 1-50 catalogue ref IDs
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(250), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    model_number = Column(String(100), nullable=True, index=True)
    manufacturer_part_number = Column(String(100), nullable=True, index=True)
    specifications = Column(JSON, default=dict)
    primary_image_url = Column(String(500), nullable=True)
    published = Column(Boolean, default=False, index=True)  # Draft by default until verified!
    featured = Column(Boolean, default=False)
    stock_status = Column(String(80), default="Contact for Availability")
    verification_notes = Column(Text, nullable=True)
    seo_title = Column(String(200), nullable=True)
    seo_description = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    compatibilities = relationship("ProductCompatibility", back_populates="product", cascade="all, delete-orphan")
    enquiries = relationship("Enquiry", back_populates="product")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=True, index=True)
    # Dimensions JSON holds: diameter_mm, inner_diameter_mm, outer_diameter_mm, length_mm, thickness_mm, bore_size, thread_size
    dimensions = Column(JSON, default=dict)
    material = Column(String(100), nullable=True)  # Cast Iron, Bronze, Stainless Steel, Gunmetal, etc.
    compatible_models = Column(String(255), nullable=True)
    price = Column(Float, nullable=True)
    quantity = Column(Integer, default=0)
    stock_status = Column(String(80), default="Contact for Price")
    image_url = Column(String(500), nullable=True)
    active = Column(Boolean, default=True)

    product = relationship("Product", back_populates="variants")
    compatibilities = relationship("ProductCompatibility", back_populates="variant")
    enquiries = relationship("Enquiry", back_populates="variant")

class ProductCompatibility(Base):
    __tablename__ = "product_compatibility"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    pump_model_id = Column(Integer, ForeignKey("pump_models.id"), nullable=False)
    compatibility_notes = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)

    product = relationship("Product", back_populates="compatibilities")
    variant = relationship("ProductVariant", back_populates="compatibilities")
    pump_model = relationship("PumpModel", back_populates="compatibilities")
