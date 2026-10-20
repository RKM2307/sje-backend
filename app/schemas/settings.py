from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class BusinessSettingsBase(BaseModel):
    business_name: str
    business_name_tamil: Optional[str] = None
    tagline: Optional[str] = None
    address: str
    city: str = "Thoothukudi"
    district: str = "Thoothukudi"
    state: str = "Tamil Nadu"
    pincode: str = "628003"
    phone: str
    landline: Optional[str] = "0461-2324374"
    alt_phone: Optional[str] = "9786009785"
    whatsapp_number: str
    email: str
    latitude: float
    longitude: float
    opening_hours: Dict[str, str]
    map_url: Optional[str] = None
    google_business_url: Optional[str] = None
    hero_heading: Optional[str] = None
    hero_subtext: Optional[str] = None
    seo_meta_title: Optional[str] = None
    seo_meta_description: Optional[str] = None

class BusinessSettingsUpdate(BaseModel):
    business_name: Optional[str] = None
    business_name_tamil: Optional[str] = None
    tagline: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    landline: Optional[str] = None
    alt_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_hours: Optional[Dict[str, str]] = None
    map_url: Optional[str] = None
    google_business_url: Optional[str] = None
    hero_heading: Optional[str] = None
    hero_subtext: Optional[str] = None
    seo_meta_title: Optional[str] = None
    seo_meta_description: Optional[str] = None

class BusinessSettingsOut(BusinessSettingsBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
