import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_all_50_reference_ids_exist():
    """Verify that all 50 reference IDs exist in the database."""
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        ref_ids = set(p.reference_number for p in products)
        expected_ids = set(range(1, 51))
        # Ensure 1 to 50 are all present
        missing = expected_ids - ref_ids
        assert len(missing) == 0, f"Missing reference IDs: {missing}"
        assert len(ref_ids) >= 50
    finally:
        db.close()

def test_admin_login():
    """Verify admin login with seeded credentials."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "Admin@Thoothukudi2024"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"

def test_search_by_ref_number():
    """Verify search by part reference number."""
    response = client.get("/api/products/ref/11")
    assert response.status_code == 200
    data = response.json()
    assert data["reference_number"] == 11
    assert "Impeller" in data["name"]
    assert len(data["variants"]) > 0

def test_prevent_duplicate_ref_id():
    """Verify duplicate reference IDs cannot be created."""
    login_res = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "Admin@Thoothukudi2024"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create duplicate for ref #11
    duplicate_payload = {
        "reference_number": 11,
        "name": "Duplicate Impeller",
        "slug": "duplicate-impeller",
        "description": "This should fail",
        "published": False
    }
    res = client.post("/api/admin/products", json=duplicate_payload, headers=headers)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]

def test_submit_product_enquiry():
    """Verify customers can submit product enquiries."""
    payload = {
        "customer_name": "Senthil Kumar",
        "phone": "+91 98421 11223",
        "email": "senthil@example.com",
        "enquiry_type": "Product Enquiry",
        "pump_brand": "PSG Pumps",
        "pump_model": "PSG OS-3",
        "quantity": 2,
        "message": "Looking for 120mm impeller for agricultural pump in Thoothukudi",
        "preferred_contact": "WhatsApp"
    }
    response = client.post("/api/enquiries", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Senthil Kumar"
    assert data["status"] == "New"

def test_business_settings():
    """Verify business settings return Thoothukudi location and details."""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["business_name"] == "Sri Jayavarman Electricals"
    assert "Thevarpuram Road" in data["address"]
    assert "Thoothukudi" in data["address"]
    assert data["latitude"] > 0
    assert data["longitude"] > 0
