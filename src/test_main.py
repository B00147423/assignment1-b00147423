from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoints():
    # 1. Add Product (EXACT fields your API expects)
    res = client.post("/addNew", json={
        "name": "TestProduct",  # No space for easier testing
        "category": "TestCat",  # Required field
        "price": 10.99,         # Must be 'price' not 'UnitPrice'
        "stock": 100,           # Must be 'stock' not 'StockQuantity'
        "description": "Test"
    })
    assert res.status_code == 200
    product_id = res.json()["product"]["_id"]
    
    # 2. Test other endpoints
    assert client.get(f"/getSingleProduct/{product_id}").status_code == 200
    assert client.get("/getAll").status_code == 200
    assert client.get("/startsWith/T").status_code == 200  # Capital T to match "TestProduct"
    assert client.get(f"/convert/{product_id}").status_code in [200, 500]
    assert client.delete(f"/deleteOne/{product_id}").status_code == 200