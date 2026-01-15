from pymongo import MongoClient
from datetime import datetime
from backend.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)

db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]


def save_run(
    email: str,
    seed_keyword: str,
    brand: str,
    market: str,
    visibility: float,
    top_3_brands: list[str]
):
    doc = {
        "email": email,
        "seed_keyword": seed_keyword,
        "brand": brand,
        "market": market,
        "visibility": visibility,
        "top_3_brands": top_3_brands,
        "created_at": datetime.utcnow()
    }

    collection.insert_one(doc)
