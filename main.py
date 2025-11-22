import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from database import db, create_document, get_documents
from schemas import FoodItem, Entry

app = FastAPI(title="Calorie Counter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Calorie Counter API is running"}

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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# --- Food Items (reference library) ---

@app.post("/api/fooditems", response_model=dict)
async def create_food_item(item: FoodItem):
    try:
        inserted_id = create_document("fooditem", item)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fooditems", response_model=List[dict])
async def list_food_items(q: Optional[str] = None, limit: int = 50):
    try:
        filter_dict = {}
        if q:
            # Basic case-insensitive substring search using regex
            filter_dict = {"name": {"$regex": q, "$options": "i"}}
        docs = get_documents("fooditem", filter_dict, limit)
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Daily Entries ---

@app.post("/api/entries", response_model=dict)
async def create_entry(entry: Entry):
    try:
        inserted_id = create_document("entry", entry)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/entries", response_model=List[dict])
async def list_entries(day: Optional[date] = None, limit: int = 200):
    try:
        filter_dict = {}
        if day:
            filter_dict = {"date": str(day)}
        docs = get_documents("entry", filter_dict, limit)
        total = 0.0
        for d in docs:
            d["id"] = str(d.pop("_id"))
            # compute calories for the entry
            qty = float(d.get("quantity", 1))
            cpu = float(d.get("calories_per_unit", 0))
            d["calories"] = round(qty * cpu, 2)
            total += d["calories"]
        return {"items": docs, "total": round(total, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary", response_model=dict)
async def summary(day: date):
    try:
        docs = get_documents("entry", {"date": str(day)}, None)
        by_meal = {"breakfast": 0.0, "lunch": 0.0, "dinner": 0.0, "snack": 0.0}
        total = 0.0
        for d in docs:
            qty = float(d.get("quantity", 1))
            cpu = float(d.get("calories_per_unit", 0))
            cal = qty * cpu
            meal = d.get("meal", "lunch")
            by_meal[meal] = by_meal.get(meal, 0.0) + cal
            total += cal
        by_meal = {k: round(v, 2) for k, v in by_meal.items()}
        return {"date": str(day), "by_meal": by_meal, "total": round(total, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
