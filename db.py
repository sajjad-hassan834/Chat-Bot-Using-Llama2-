from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["Main_DB"]  # Replace with your actual database name
collection1 = db["User_Detail"]  # Replace with your actual collection name
collection2 = db["Conversation_Detail"]  # Replace with your actual collection name


def create(data):
    result = collection1.insert_one(data.model_dump())
    return str(result.inserted_id)  


def get_user_history(user_id):
    return list(collection2.find({"user_id": user_id}, {"_id": 0}))
