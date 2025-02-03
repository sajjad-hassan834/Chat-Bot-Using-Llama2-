import ollama
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from pymongo.errors import PyMongoError
import logging
from schema import UserCreate, UserHistory, Message
from db import collection1, collection2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_collection1():
    return collection1

def get_collection2():
    return collection2

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/create", response_model=UserCreate)
def create_user(user: UserCreate, collection1=Depends(get_collection1)):
    try:
        user_dict = user.dict()
        result = collection1.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        return user_dict
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@app.get("/history/{user_id}", response_model=UserHistory)
def get_history(user_id: int, collection2=Depends(get_collection2)):
    try:
        history = list(collection2.find({"user_id": user_id}, {"_id": 0}))
        if not history:
            raise HTTPException(status_code=404, detail="No history found for this user")
        return {"user_id": user_id, "history": history}
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

def get_user_history(user_id: int, collection2) -> List[dict]:
    """
    Retrieve the user's previous messages and responses from MongoDB.
    """
    history = list(collection2.find({"user_id": user_id}, {"_id": 0}))
    return history

def llama2_local_response(user_id: int, message: str, collection2) -> str:
    """
    Send the message along with user history to LLaMA 3.2 via Ollama.
    """
    try:
        # Retrieve previous conversations
        history = get_user_history(user_id, collection2)
        
        # Format messages in Ollama-compatible structure
        messages = [{"role": "system", "content": "You are an AI assistant."}]
        for convo in history:
            messages.append({"role": "user", "content": convo["message"]})
            messages.append({"role": "assistant", "content": convo["response"]})

        # Append the new user message
        messages.append({"role": "user", "content": message})

        # Send to LLaMA model
        response = ollama.chat(model="llama3.2", messages=messages)
        return response["message"]["content"]

    except Exception as e:
        logger.error(f"LLaMA model error: {e}")
        return "Error generating response."

@app.get("/api/message/{user_id}", response_model=Message)
async def handle_message(user_id: int, message_id: int, message: str, collection2=Depends(get_collection2)):
    try:
        # Generate response using Ollama (LLaMA 3.2) with history
        response_text = llama2_local_response(user_id, message, collection2)

        # Create a new conversation object
        new_conversation = Message(
            user_id=user_id,
            message_id=message_id,
            message=message,
            response=response_text
        )

        # Insert into MongoDB
        collection2.insert_one(new_conversation.dict())
        return new_conversation
    
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to store message")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")
