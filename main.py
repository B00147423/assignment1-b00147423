from fastapi import FastAPI, HTTPException, Query, Path, Depends
from pymongo import MongoClient
from pydantic import BaseModel, Field
import requests
from bson import ObjectId

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://admin:pass@localhost:27017/?authSource=admin")
db = client["WebServices"]
collection = db["products"]


class Product(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str

class PaginationParams(BaseModel):
    start_id: int = Field(..., ge=0)
    end_id: int = Field(..., gt=0)


@app.get("/getSingleProduct/{product_id}")
def get_single_product(product_id: str = Path(..., title="MongoDB Object ID")):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    product = collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Convert the entire product document, including all fields
    product["product_id"] = str(product["_id"])
    del product["_id"]  # Remove the raw _id
    return product  # This will include name, category, etc.



@app.get("/getAll")
def get_all_products():
    products = list(collection.find({}))
    for product in products:
        product["_id"] = str(product["_id"])
    return products

@app.post("/addNew")
def add_new_product(product: Product):
    product_dict = product.dict()
    result = collection.insert_one(product_dict)

    # Add Mongo-generated ID back into response, converted to string
    product_dict["_id"] = str(result.inserted_id)

    return {
        "message": "Product added successfully",
        "product": product_dict
    }


@app.delete("/deleteOne/{product_id}")
def delete_product(product_id: str = Path(..., title="MongoDB Object ID")):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    result = collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}


@app.get("/startsWith/{letter}")
def starts_with(letter: str = Path(..., min_length=1, max_length=1, title="Single letter")):
    # Make sure the letter is being received correctly
    print(f"Searching for products that start with: {letter}")

    products = list(collection.find({"name": {"$regex": f"^{letter}", "$options": "i"}}, {"_id": 0}))

    if not products:
        print("No products found.")

    return products


@app.get("/paginate")
def paginate(start_id: str = Query(...), end_id: str = Query(...)):
    from bson import ObjectId

    if not ObjectId.is_valid(start_id) or not ObjectId.is_valid(end_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    
    start = ObjectId(start_id)
    end = ObjectId(end_id)

    products = list(
        collection.find({"_id": {"$gte": start, "$lte": end}}, {"_id": 0}).limit(10)
    )
    return products

@app.get("/convert/{product_id}")
def convert_price(product_id: str = Path(..., title="MongoDB Object ID")):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    product = collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    price = product.get("price") or product.get("Unit Price")
    if not price:
        raise HTTPException(status_code=400, detail="Product has no price field")

    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get exchange rate")

    exchange_rate = response.json()["rates"]["EUR"]
    converted_price = price * exchange_rate
    return {"product_id": product_id, "price_in_euro": round(converted_price, 2)}
