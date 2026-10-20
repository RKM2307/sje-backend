import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sri Jayavarman Electricals"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shop.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sri-jayavarman-electricals-production-secret-key-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Uploads
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Business verified info from storefront signboard
    BUSINESS_NAME: str = "Sri Jayavarman Electricals"
    BUSINESS_NAME_TAMIL: str = "ஸ்ரீ ஜெயவர்மன் எலக்ட்ரிக்கல்ஸ் (ராஜீ எலக்ட்ரிக்கல் சர்வீஸ் - அங்கம்)"
    BUSINESS_ADDRESS: str = "93A, Thevarpuram Road, Thoothukudi - 628003, Tamil Nadu, India"
    DEFAULT_PHONE: str = "9442535457"
    DEFAULT_LANDLINE: str = "0461-2324374"
    DEFAULT_ALT_PHONE: str = "9786009783"
    DEFAULT_WHATSAPP: str = "9442535457"
    DEFAULT_EMAIL: str = "contact@srijayavarmanelectricals.com"
    DEFAULT_LATITUDE: float = 8.8078
    DEFAULT_LONGITUDE: float = 78.1465

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
