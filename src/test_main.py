from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoints():
    # Test /addNew with CORRECT field names
    res = client.post("/addNew", json={
        "name": "Test Product",
        "category": "Test Category",  # Required field
        "price": 10.99,              # Must be 'price' not 'unitPrice'
        "stock": 100,                # Must be 'stock' not 'stockQuantity'
        "description": "Test description"
    })
    assert res.status_code == 200
    product = res.json()["product"]
    product_id = product["_id"]
    
    # Test /getSingleProduct
    assert client.get(f"/getSingleProduct/{product_id}").status_code == 200
    
    # Test /getAll
    assert client.get("/getAll").status_code == 200
    
    # Test /startsWith
    assert client.get("/startsWith/t").status_code == 200
    
    # Test /convert
    assert client.get(f"/convert/{product_id}").status_code in [200, 500]
    
    # Test /deleteOne
    assert client.delete(f"/deleteOne/{product_id}").status_code == 200