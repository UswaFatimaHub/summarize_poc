from pymongo import MongoClient
from app.config import get_settings
from bson.objectid import ObjectId
from app.utils.cleaning import clean_text_column
import pandas as pd

settings = get_settings()

client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

def insert_csv_to_mongo(csv_path: str, collection_name: str = "conversations"):
    try:
        df = pd.read_csv(csv_path)
        df = clean_text_column(df)
        df.dropna(how="all", inplace=True)
        records = df.to_dict(orient="records")
        
        if records:
            result = db[collection_name].insert_many(records)
            return {"inserted_count": len(result.inserted_ids)}
        else:
            return {"inserted_count": 0, "message": "No records found in CSV"}
    except Exception as e:
        return {"error": str(e)}

def purge_collection():
    collection_name = "conversations"
    try:
        if collection_name not in db.list_collection_names():
            raise ValueError(f"Collection '{collection_name}' does not exist.")
        
        result = db[collection_name].delete_many({})
        return {"deleted_count": result.deleted_count}
    except Exception as e:
        return {"error": str(e)}
    

def get_records_by_opportunity_id(opportunity_id: float):
    try:
        # Query MongoDB for records with the specified opportunity_id
        records_cursor = db.conversations.find(
            {"opportunity_id": opportunity_id},  # Filter by opportunity_id
            {"_id": 0, "date": 1, "opportunity_id": 1, "text": 1, "user_id": 1}  # Only retrieve specified fields
        ).sort("date", 1)  # Sort by date in ascending order
        
        records = list(records_cursor)
        total_records = len(records)  # Count the total number of records retrieved
        
        return {"total_records": total_records, "records": records}
    except Exception as e:
        return {"error": str(e)}
