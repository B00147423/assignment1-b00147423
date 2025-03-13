import requests

BASE_URL = "http://localhost:8000"

def test_get_all():
    response = requests.get(f"{BASE_URL}/getAll")
    assert response.status_code == 200

def test_add_new():
    product = {
        "name": "Test Product",
        "category": "Test",
        "price": 10.99,
        "stock": 5,
        "description": "A sample product"
    }
    response = requests.post(f"{BASE_URL}/addNew", json=product)
    assert response.status_code == 200

def test_convert():
    response = requests.get(f"{BASE_URL}/convert/1")
    assert response.status_code == 200
