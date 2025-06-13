from pymongo import MongoClient
from app.config import get_settings
from bson.objectid import ObjectId

settings = get_settings()

client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

def create_conversation(data: dict) -> str:
    result = db.conversations.insert_one(data)
    return str(result.inserted_id)


def get_all_conversations():
    conversations = list(db.conversations.find({}, {"_id": 0}))
    return conversations

def get_conversation_by_id(convo_id: str):
    convo = db.conversations.find_one({"_id": ObjectId(convo_id)})
    if convo:
        convo["id"] = str(convo["_id"])
        del convo["_id"]
    return convo

def update_conversation(convo_id: str, update_data: dict) -> bool:
    result = db.conversations.update_one(
        {"_id": ObjectId(convo_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0
