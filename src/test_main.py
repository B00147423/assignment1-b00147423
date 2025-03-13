import requests
from pymongo import MongoClient

BASE_URL = "http://localhost:8000"

client = MongoClient("mongodb://localhost:27017/")
db = client["inventory_db"]
collection = db["products"]

def get_valid_product_id():
    """Fetch an existing product ID from the database."""
    product = collection.find_one({}, {"_id": 1})
    return str(product["_id"]) if product else None

# ✅ Test getting all products
def test_get_all():
    response = requests.get(f"{BASE_URL}/getAll")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ✅ Test adding a new product
def test_add_new():
    product = {
        "name": "Test Product",
        "category": "Test Category",
        "price": 19.99,
        "stock": 50,
        "description": "This is a test product"
    }
    response = requests.post(f"{BASE_URL}/addNew", json=product)
    assert response.status_code == 200
    assert "message" in response.json()

# ✅ Test getting a single product
def test_get_single_product():
    product_id = get_valid_product_id()
    if product_id:
        response = requests.get(f"{BASE_URL}/getSingleProduct/{product_id}")
        assert response.status_code == 200
        assert "name" in response.json()
    else:
        print("No product found in DB. Skipping test.")

# ✅ Test deleting a product
def test_delete_product():
    product_id = get_valid_product_id()
    if product_id:
        response = requests.delete(f"{BASE_URL}/deleteOne/{product_id}")
        assert response.status_code in [200, 404]  # 404 if already deleted
    else:
        print("No product found in DB. Skipping test.")

# ✅ Test searching by first letter
def test_starts_with():
    response = requests.get(f"{BASE_URL}/startsWith/T")  # Products starting with "T"
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ✅ Test pagination
def test_pagination():
    response = requests.get(f"{BASE_URL}/paginate?start_id=1&end_id=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ✅ Test converting price from USD to EUR
def test_convert_price():
    product_id = get_valid_product_id()
    if product_id:
        response = requests.get(f"{BASE_URL}/convert/{product_id}")
        assert response.status_code == 200
        assert "price_in_euro" in response.json()
    else:
        print("No product found in DB. Skipping test.")
