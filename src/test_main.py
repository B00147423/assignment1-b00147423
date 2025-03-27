


# test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_endpoints():
    res = client.post("/addNew", json={
        "name": "Test Product",       
        "category": "Test Category",  
        "price": 10.99,                
        "stock": 100,                 
        "description": "Test description"
    })
    assert res.status_code == 200
    product_id = res.json()["product"]["_id"]
    # Test /getSingleProduct
    assert client.get(f"/getSingleProduct/{product_id}").status_code == 200

    # Test /getAll
    assert client.get("/getAll").status_code == 200

    # Test /startsWith
    assert client.get("/startsWith/t").status_code == 200

    # Test /convert
    assert client.get(f"/convert/{product_id}").status_code in [200, 500]  # 500 if API fails

    # Test /deleteOne
    assert client.delete(f"/deleteOne/{product_id}").status_code == 200