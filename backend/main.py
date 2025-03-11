from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import List

# Initialize FastAPI app
app = FastAPI()

# CORS settings to allow specific origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to specific origins like ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["flashcard_db"]
flashcards_collection = db["flashcards"]

# Pydantic model for Flashcard
class Flashcard(BaseModel):
    question: str
    answer: str

class FlashcardInDB(Flashcard):
    id: str

# Endpoint to create a new flashcard
@app.post("/flashcards/", response_model=FlashcardInDB)
async def create_flashcard(flashcard: Flashcard):
    result = flashcards_collection.insert_one(flashcard.dict())
    new_flashcard = flashcard.dict()
    new_flashcard['id'] = str(result.inserted_id)
    return new_flashcard

# Endpoint to get all flashcards
@app.get("/flashcards/", response_model=List[FlashcardInDB])
async def get_flashcards():
    flashcards = []
    for flashcard in flashcards_collection.find():
        flashcards.append({"id": str(flashcard["_id"]), "question": flashcard["question"], "answer": flashcard["answer"]})
    return flashcards

# Endpoint to get a flashcard by id
@app.get("/flashcards/{flashcard_id}", response_model=FlashcardInDB)
async def get_flashcard(flashcard_id: str):
    flashcard = flashcards_collection.find_one({"_id": ObjectId(flashcard_id)})
    if flashcard is None:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return {"id": str(flashcard["_id"]), "question": flashcard["question"], "answer": flashcard["answer"]}

# Endpoint to update a flashcard by id
@app.put("/flashcards/{flashcard_id}", response_model=FlashcardInDB)
async def update_flashcard(flashcard_id: str, flashcard: Flashcard):
    result = flashcards_collection.update_one(
        {"_id": ObjectId(flashcard_id)},
        {"$set": flashcard.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    updated_flashcard = flashcards_collection.find_one({"_id": ObjectId(flashcard_id)})
    return {"id": str(updated_flashcard["_id"]), "question": updated_flashcard["question"], "answer": updated_flashcard["answer"]}

@app.delete("/flashcards/{flashcard_id}")
async def delete_flashcard(flashcard_id: str):
    result = flashcards_collection.delete_one({"_id": ObjectId(flashcard_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return {"message": "Flashcard deleted successfully"}
