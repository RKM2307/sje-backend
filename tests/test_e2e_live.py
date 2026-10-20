import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_live_health():
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    print("[PASS] Live health check")

def test_live_admin_login():
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "Admin@Thoothukudi2024"
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token is not None
    print("[PASS] Live admin login")
    return token

def test_all_50_reference_ids(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/admin/products?limit=100", headers=headers)
    assert res.status_code == 200
    data = res.json()
    items = data["items"]
    assert len(items) >= 50, f"Expected at least 50 items, got {len(items)}"
    
    ref_numbers = set(p["reference_number"] for p in items)
    for i in range(1, 51):
        assert i in ref_numbers, f"Reference #{i} is missing!"
    print(f"[PASS] All 50 reference IDs (1-50) exist in database! Total count: {len(items)}")

def test_product_detail_and_variants():
    res = requests.get(f"{BASE_URL}/products/ref/11")
    assert res.status_code == 200
    data = res.json()
    assert data["reference_number"] == 11
    assert "Impeller" in data["name"]
    assert len(data["variants"]) >= 3
    print(f"[PASS] Product Ref #11 (Impeller) verified with {len(data['variants'])} variants")

def test_csv_export(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/admin/export-csv", headers=headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    csv_text = res.text
    assert "Reference ID" in csv_text
    assert "Product Name" in csv_text
    assert "Diameter (mm)" in csv_text
    print("[PASS] CSV inventory template export verified")

def test_enquiry_submission():
    payload = {
        "customer_name": "Kandasamy M.",
        "phone": "+91 94421 88990",
        "enquiry_type": "Spare Part Identification",
        "pump_brand": "PSG Pumps",
        "pump_model": "PSG OS-3",
        "quantity": 1,
        "message": "Need 120mm Gunmetal impeller for openwell pump",
        "preferred_contact": "WhatsApp"
    }
    res = requests.post(f"{BASE_URL}/enquiries", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["customer_name"] == "Kandasamy M."
    print("[PASS] Enquiry submission verified")

if __name__ == "__main__":
    test_live_health()
    tok = test_live_admin_login()
    test_all_50_reference_ids(tok)
    test_product_detail_and_variants()
    test_csv_export(tok)
    test_enquiry_submission()
    print("\nALL LIVE ACCEPTANCE VERIFICATIONS PASSED SUCCESSFULLY!")
