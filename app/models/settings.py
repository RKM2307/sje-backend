import datetime
from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime
from app.database import Base

class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(200), default="Sri Jayavarman Electricals")
    business_name_tamil = Column(String(250), default="ஸ்ரீ ஜெயவர்மன் எலக்ட்ரிக்கல்ஸ் (ராஜீ எலக்ட்ரிக்கல் சர்வீஸ் - அங்கம்)")
    tagline = Column(String(300), default="PSG & CRI Pumps, Motors and Spare Parts in Thoothukudi")
    address = Column(Text, default="93A, Thevarpuram Road, Thoothukudi - 628003, Tamil Nadu, India")
    city = Column(String(100), default="Thoothukudi")
    district = Column(String(100), default="Thoothukudi")
    state = Column(String(100), default="Tamil Nadu")
    pincode = Column(String(20), default="628003")
    phone = Column(String(50), default="9442535457")
    landline = Column(String(50), default="0461-2324374")
    alt_phone = Column(String(50), default="9786009785")
    whatsapp_number = Column(String(50), default="9442535457")
    email = Column(String(120), default="contact@srijayavarmanelectricals.com")
    latitude = Column(Float, default=8.8078)
    longitude = Column(Float, default=78.1465)
    opening_hours = Column(JSON, default=lambda: {
        "Monday": "9:00 AM - 8:30 PM",
        "Tuesday": "9:00 AM - 8:30 PM",
        "Wednesday": "9:00 AM - 8:30 PM",
        "Thursday": "9:00 AM - 8:30 PM",
        "Friday": "9:00 AM - 8:30 PM",
        "Saturday": "9:00 AM - 8:30 PM",
        "Sunday": "Closed / Emergency Enquiries"
    })
    map_url = Column(Text, default="https://maps.google.com/?q=8.8078,78.1465")
    google_business_url = Column(Text, nullable=True)
    hero_heading = Column(String(250), default="PSG & CRI Pumps, Motors and Spare Parts in Thoothukudi")
    hero_subtext = Column(Text, default="Explore pump assemblies, motor components, impellers, shafts, bearings, seals, valves and related spare parts. Contact Sri Jayavarman Electricals on Thevarpuram Road for direct assistance.")
    seo_meta_title = Column(String(200), default="Sri Jayavarman Electricals | PSG & CRI Pumps & Spares Thoothukudi")
    seo_meta_description = Column(String(300), default="Genuine pump & motor spare parts dealer on Thevarpuram Road, Thoothukudi (Tuticorin). Call 94425 35457.")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
