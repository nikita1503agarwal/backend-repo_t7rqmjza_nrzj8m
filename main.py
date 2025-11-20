import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from bson import ObjectId

from schemas import Product, Order
from database import db, create_document, get_documents

app = FastAPI(title="Katalyst Apparels API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Katalyst Apparels Backend Running"}

@app.get("/schema")
def get_schema():
    """Expose schemas for tooling"""
    return {
        "collections": [
            "product",
            "order",
        ]
    }

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "❌ Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ---- Products ----
@app.post("/api/products", response_model=dict)
async def create_product(product: Product):
    try:
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products", response_model=List[dict])
async def list_products(tag: Optional[str] = None, featured: Optional[bool] = None, limit: int = 50):
    try:
        query = {}
        if tag:
            query["tags"] = {"$in": [tag]}
        if featured is not None:
            query["is_featured"] = featured
        docs = get_documents("product", query, limit=limit)
        # Convert ObjectId to string
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=dict)
async def get_product(product_id: str):
    try:
        doc = db["product"].find_one({"_id": ObjectId(product_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/seed")
async def seed_products():
    """Seed a few demo jerseys if none exist"""
    try:
        count = db["product"].count_documents({}) if db else 0
        if count > 0:
            return {"inserted": 0, "message": "Products already exist"}
        demo = [
            {
                "title": "Arsenal Home Jersey 24/25",
                "team": "Arsenal",
                "league": "Premier League",
                "season": "24/25",
                "description": "Breathable match-inspired jersey in classic red.",
                "price": 89.0,
                "currency": "USD",
                "sizes": ["S","M","L","XL"],
                "images": [
                    "https://images.unsplash.com/photo-1590151773968-6e1da383b64e?q=80&w=1200&auto=format&fit=crop"
                ],
                "in_stock": True,
                "is_featured": True,
                "tags": ["arsenal","home","24/25","red"],
                "colorway": "red"
            },
            {
                "title": "Real Madrid Away Jersey 24/25",
                "team": "Real Madrid",
                "league": "La Liga",
                "season": "24/25",
                "description": "Crisp away shirt with moisture-wicking fabric.",
                "price": 95.0,
                "currency": "USD",
                "sizes": ["S","M","L","XL"],
                "images": [
                    "https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=1200&auto=format&fit=crop"
                ],
                "in_stock": True,
                "is_featured": False,
                "tags": ["real madrid","away","24/25","white"],
                "colorway": "white"
            },
            {
                "title": "Inter Miami Home Jersey 24/25",
                "team": "Inter Miami",
                "league": "MLS",
                "season": "24/25",
                "description": "Signature pink design inspired by the Miami skyline.",
                "price": 99.0,
                "currency": "USD",
                "sizes": ["S","M","L","XL"],
                "images": [
                    "https://images.unsplash.com/photo-1520971347561-84524d5a31e1?q=80&w=1200&auto=format&fit=crop"
                ],
                "in_stock": True,
                "is_featured": True,
                "tags": ["miami","home","24/25","pink"],
                "colorway": "pink"
            }
        ]
        inserted = db["product"].insert_many(demo)
        return {"inserted": len(inserted.inserted_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- Orders ----
@app.post("/api/orders", response_model=dict)
async def create_order(order: Order):
    try:
        inserted_id = create_document("order", order)
        return {"id": inserted_id, "status": order.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
