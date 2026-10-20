from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.settings import BusinessSettings
from app.models.user import AdminUser
from app.schemas.settings import BusinessSettingsOut, BusinessSettingsUpdate
from app.services.auth import get_current_admin_user

router = APIRouter(prefix="/settings", tags=["Business Settings"])

def get_or_create_settings(db: Session) -> BusinessSettings:
    settings = db.query(BusinessSettings).first()
    if not settings:
        settings = BusinessSettings(
            business_name="Sri Jayavarman Electricals",
            business_name_tamil="ஸ்ரீ ஜெயவர்மன் எலக்ட்ரிக்கல்ஸ் (ராஜீ எலக்ட்ரிக்கல் சர்வீஸ் - அங்கம்)",
            tagline="PSG & CRI Pumps, Motors and Spare Parts in Thoothukudi",
            address="93A, Thevarpuram Road, Thoothukudi - 628003, Tamil Nadu, India",
            city="Thoothukudi",
            district="Thoothukudi",
            state="Tamil Nadu",
            pincode="628003",
            phone="9442535457",
            landline="0461-2324374",
            alt_phone="9786009785",
            whatsapp_number="9442535457",
            email="contact@srijayavarmanelectricals.com",
            latitude=8.8078,
            longitude=78.1465,
            opening_hours={
                "Monday": "9:00 AM - 8:30 PM",
                "Tuesday": "9:00 AM - 8:30 PM",
                "Wednesday": "9:00 AM - 8:30 PM",
                "Thursday": "9:00 AM - 8:30 PM",
                "Friday": "9:00 AM - 8:30 PM",
                "Saturday": "9:00 AM - 8:30 PM",
                "Sunday": "Closed / Emergency Enquiries"
            },
            map_url="https://maps.google.com/?q=8.8078,78.1465",
            hero_heading="PSG & CRI Pumps, Motors and Spare Parts in Thoothukudi",
            hero_subtext="Explore pump assemblies, motor components, impellers, shafts, bearings, seals, valves and related spare parts. Contact Sri Jayavarman Electricals directly on Thevarpuram Road.",
            seo_meta_title="Sri Jayavarman Electricals | PSG & CRI Pumps & Spares Thoothukudi",
            seo_meta_description="Leading pump & motor dealer on Thevarpuram Road, Thoothukudi. Genuine pump spare parts, impellers, shafts, bearings, and motor servicing. Call 94425 35457."
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    else:
        # Ensure updated phone numbers are in place
        if settings.phone != "9442535457" or not getattr(settings, 'business_name_tamil', None):
            settings.phone = "9442535457"
            settings.whatsapp_number = "9442535457"
            settings.landline = "0461-2324374"
            settings.alt_phone = "9786009785"
            settings.pincode = "628003"
            settings.business_name_tamil = "ஸ்ரீ ஜெயவர்மன் எலக்ட்ரிக்கல்ஸ் (ராஜீ எலக்ட்ரிக்கல் சர்வீஸ் - அங்கம்)"
            db.commit()
            db.refresh(settings)

    return settings

@router.get("", response_model=BusinessSettingsOut)
def get_public_settings(db: Session = Depends(get_db)):
    return get_or_create_settings(db)

@router.put("", response_model=BusinessSettingsOut)
def update_settings(
    data: BusinessSettingsUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    settings = get_or_create_settings(db)
    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(settings, field, val)

    db.commit()
    db.refresh(settings)
    return settings
