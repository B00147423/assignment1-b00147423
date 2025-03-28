# readme.py

with open("README.txt", "w") as f:
    f.write("""API Endpoints:
- GET /getSingleProduct/{product_id}
- GET /getAll
- POST /addNew
- DELETE /deleteOne/{product_id}
- GET /startsWith/{letter}
- GET /paginate?start_id=...&end_id=...
- GET /convert/{product_id}
""")