from typing import Union

from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel
import requests
import os
from bson.objectid import ObjectId

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["inventory_db"]
collection = db["products"]

class Product(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    description: str

    # get: single product
@app.get("/getSingleProduct/{product_id}")
def get_single_product(product_id: str):
    product = collection.find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# get: all products
@app.get("/getAllProducts")
def get_all_products():
    products = list(collection.find({}, {"_id": 0}))
    return products

@app.post("/addNewProduct")
def addNewProduct(product: Product):
    product_dict = product.dict()
    collection.insert_one(product_dict)
    return {"message": "Product added successfully", "product": product_dict}

# DELETE: Remove a product by ID
@app.delete("/deleteOne/{product_id}")
def deleteProduct(product_id: str):
    try:
        if not ObjectId.is_valid(product_id):  # Validate ObjectId format
            raise HTTPException(status_code=400, detail="Invalid product ID format")

        result = collection.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET: Retrieve products starting with a letter
@app.get("/startsWith/{letter}")
def startsWith(letter: str):
    products = list(collection.find({"name": {"$regex": f"^{letter}", "$options": "i"}}, {"_id": 0}))
    return products

# GET: Paginate products
@app.get("/paginate")
def paginate(start_id: str, end_id: str):
    products = list(collection.find({"_id": {"$gte": start_id, "$lte": end_id}}, {"_id": 0}).limit(10))
    return products

# GET: Convert price from USD to EUR
@app.get("/convert/{product_id}")
def convertPrice(product_id: str):
    product = collection.find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Fetch exchange rate
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get exchange rate")

    exchange_rate = response.json()["rates"]["EUR"]
    converted_price = product["price"] * exchange_rate
    return {"product_id": product_id, "price_in_euro": round(converted_price, 2)}