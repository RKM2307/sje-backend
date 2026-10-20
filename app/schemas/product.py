from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_category_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    product_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Brand Schemas
class BrandBase(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    authorisation_status: Optional[str] = "Authorisation Pending Verification"
    description: Optional[str] = None
    active: bool = True

class BrandCreate(BrandBase):
    pass

class BrandOut(BrandBase):
    id: int
    product_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Pump Model Schemas
class PumpModelBase(BaseModel):
    brand_id: int
    model_name: str
    model_number: Optional[str] = None
    pump_type: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = {}
    active: bool = True

class PumpModelCreate(PumpModelBase):
    pass

class PumpModelOut(PumpModelBase):
    id: int
    brand_name: Optional[str] = None

    class Config:
        from_attributes = True

# Product Variant Schemas
class ProductVariantBase(BaseModel):
    variant_name: str
    sku: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = {}
    material: Optional[str] = None
    compatible_models: Optional[str] = None
    price: Optional[float] = None
    quantity: int = 0
    stock_status: Optional[str] = "Contact for Price"
    image_url: Optional[str] = None
    active: bool = True

class ProductVariantCreate(ProductVariantBase):
    product_id: Optional[int] = None

class ProductVariantUpdate(BaseModel):
    variant_name: Optional[str] = None
    sku: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    material: Optional[str] = None
    compatible_models: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    stock_status: Optional[str] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None

class ProductVariantOut(ProductVariantBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True

# Compatibility Schemas
class CompatibilityCreate(BaseModel):
    product_id: int
    pump_model_id: int
    variant_id: Optional[int] = None
    compatibility_notes: Optional[str] = None
    verified: bool = False

class CompatibilityOut(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int] = None
    pump_model_id: int
    model_name: Optional[str] = None
    brand_name: Optional[str] = None
    pump_type: Optional[str] = None
    compatibility_notes: Optional[str] = None
    verified: bool

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    reference_number: int  # Original 1-50 catalogue ID
    name: str
    slug: str
    description: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    model_number: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = {}
    primary_image_url: Optional[str] = None
    published: bool = False
    featured: bool = False
    stock_status: Optional[str] = "Contact for Availability"
    verification_notes: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    reference_number: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    model_number: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    primary_image_url: Optional[str] = None
    published: Optional[bool] = None
    featured: Optional[bool] = None
    stock_status: Optional[str] = None
    verification_notes: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

class ProductListItem(BaseModel):
    id: int
    reference_number: int
    name: str
    slug: str
    description: Optional[str] = None
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    primary_image_url: Optional[str] = None
    published: bool
    featured: bool
    stock_status: str
    variant_count: int = 0
    starting_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductDetailOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    brand: Optional[BrandOut] = None
    category: Optional[CategoryOut] = None
    variants: List[ProductVariantOut] = []
    compatibilities: List[CompatibilityOut] = []

    class Config:
        from_attributes = True

class PaginatedProducts(BaseModel):
    items: List[ProductListItem]
    total: int
    page: int
    limit: int
    total_pages: int
