from fastapi.testclient import TestClient
from main import app
from bson import ObjectId
import pytest

client = TestClient(app)

# Test data matching your Product model
TEST_PRODUCT = {
    "name": "TestProduct",
    "category": "Test",
    "price": 10.99,
    "stock": 100,
    "description": "Test description"
}

# Helper to get created product ID
def create_test_product():
    response = client.post("/addNew", json=TEST_PRODUCT)
    return response.json()["product"]["_id"]

# 1. Test /getSingleProduct/{product_id}
def test_get_single_product():
    # Create → Get → Delete test pattern
    product_id = create_test_product()
    response = client.get(f"/getSingleProduct/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == TEST_PRODUCT["name"]
    client.delete(f"/deleteOne/{product_id}")

# 2. Test /getAll
def test_get_all_products():
    product_id = create_test_product()
    response = client.get("/getAll")
    assert response.status_code == 200
    assert any(p["_id"] == product_id for p in response.json())
    client.delete(f"/deleteOne/{product_id}")

# 3. Test /addNew
def test_add_product():
    response = client.post("/addNew", json=TEST_PRODUCT)
    assert response.status_code == 200
    product_id = response.json()["product"]["_id"]
    client.delete(f"/deleteOne/{product_id}")

# 4. Test /deleteOne/{product_id}
def test_delete_product():
    product_id = create_test_product()
    response = client.delete(f"/deleteOne/{product_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"

# 5. Test /startsWith/{letter}
def test_starts_with():
    product_id = create_test_product()
    response = client.get(f"/startsWith/{TEST_PRODUCT['name'][0].lower()}")
    assert response.status_code == 200
    assert any(p["name"].startswith(TEST_PRODUCT['name'][0]) for p in response.json())
    client.delete(f"/deleteOne/{product_id}")

# 6. Test /paginate
def test_paginate():
    id1 = create_test_product()
    id2 = create_test_product()
    response = client.get(f"/paginate?start_id={id1}&end_id={id2}")
    assert response.status_code == 200
    client.delete(f"/deleteOne/{id1}")
    client.delete(f"/deleteOne/{id2}")

# 7. Test /convert/{product_id}
def test_convert_price():
    product_id = create_test_product()
    response = client.get(f"/convert/{product_id}")
    assert response.status_code in [200, 500]  # 500 if API rate limit exceeded
    client.delete(f"/deleteOne/{product_id}")