from fastapi import FastAPI, HTTPException, Query, Path, Depends
from pymongo import MongoClient
from pydantic import BaseModel, Field
import requests
from bson import ObjectId

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/?authSource=admin")
db = client["WebServices"]
collection = db["products"]

# ✅ Pydantic Model for adding new product
class Product(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str

# ✅ Pydantic Model for pagination parameters
class PaginationParams(BaseModel):
    start_id: int = Field(..., ge=0)
    end_id: int = Field(..., gt=0)

# ✅ Get a single product (ID validated)
@app.get("/getSingleProduct/{product_id}")
def get_single_product(product_id: str = Path(..., title="MongoDB Object ID")):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    product = collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

# ✅ Get all products
@app.get("/getAll")
def get_all_products():
    return list(collection.find({}, {"_id": 0}))

# ✅ Add a new product
@app.post("/addNew")
def add_new_product(product: Product):
    product_dict = product.dict()
    collection.insert_one(product_dict)
    return {"message": "Product added successfully", "product": product_dict}

# ✅ Delete a product by ID
@app.delete("/deleteOne/{product_id}")
def delete_product(product_id: str = Path(..., title="MongoDB Object ID")):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    result = collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}

# ✅ Get products starting with a specific letter
@app.get("/startsWith/{letter}")
def starts_with(letter: str = Path(..., min_length=1, max_length=1, title="Single letter")):
    products = list(collection.find({"name": {"$regex": f"^{letter}", "$options": "i"}}, {"_id": 0}))
    return products

# ✅ Paginate products by ID range
@app.get("/paginate")
def paginate(params: PaginationParams = Depends()):
    products = list(
        collection.find({"_id": {"$gte": params.start_id, "$lte": params.end_id}}, {"_id": 0}).limit(10)
    )
    return products

# ✅ Convert price from USD to EUR
@app.get("/convert/{product_id}")
def convert_price(product_id: str = Path(..., title="MongoDB Object ID")):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    product = collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get exchange rate")

    exchange_rate = response.json()["rates"]["EUR"]
    converted_price = product["price"] * exchange_rate
    return {"product_id": product_id, "price_in_euro": round(converted_price, 2)}
