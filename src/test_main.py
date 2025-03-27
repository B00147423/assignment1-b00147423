import requests
from pymongo import MongoClient
from pydantic import BaseModel
BASE_URL = "http://localhost:8000"

client = MongoClient("mongodb://localhost:27017/")
db = client["inventory_db"]
collection = db["products"]

def get_valid_product_id():
    """Fetch an existing product ID from the database."""
    product = collection.find_one({}, {"_id": 1})
    return str(product["_id"]) if product else None

def test_get_all():
    response = requests.get(f"{BASE_URL}/getAll")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_new():
    global added_product_id
    product = {
        "name": "Test Product",
        "category": "Test Category",
        "price": 19.99,
        "stock": 50,
        "description": "This is a test product"
    }
    response = requests.post(f"{BASE_URL}/addNew", json=product)
    assert response.status_code == 200
    added_product_id = collection.find_one({"name": "Test Product"})["_id"]

def test_get_single_product():
    product_id = get_valid_product_id()
    if product_id:
        response = requests.get(f"{BASE_URL}/getSingleProduct/{product_id}")
        assert response.status_code == 200
        assert "name" in response.json()
    else:
        print("No product found in DB. Skipping test.")

def test_delete_product():
    product_id = get_valid_product_id()
    if product_id:
        response = requests.delete(f"{BASE_URL}/deleteOne/{product_id}")
        assert response.status_code in [200, 404]  # 404 if already deleted
    else:
        print("No product found in DB. Skipping test.")

def test_starts_with():
    response = requests.get(f"{BASE_URL}/startsWith/T")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_pagination():
    ids = list(collection.find({}, {"_id": 1}).limit(2))
    if len(ids) == 2:
        start_id = str(ids[0]["_id"])
        end_id = str(ids[1]["_id"])
        response = requests.get(f"{BASE_URL}/paginate?start_id={start_id}&end_id={end_id}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    else:
        print("Not enough data for pagination test.")

def test_convert_price():
    product_id = get_valid_product_id()
    if product_id:
        response = requests.get(f"{BASE_URL}/convert/{product_id}")
        assert response.status_code == 200
        assert "price_in_euro" in response.json()
    else:
        print("No product found in DB. Skipping test.")


if __name__ == "__main__":
    test_get_all()
    test_add_new()
    test_get_single_product()
    test_delete_product()
    test_starts_with()
    test_pagination()
    test_convert_price()
    print("✅ All tests executed.")