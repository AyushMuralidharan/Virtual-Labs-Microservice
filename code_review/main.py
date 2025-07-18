from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from pymongo import MongoClient
import logging
from code_review.utils.service_health import service_health
from code_review.middleware.service_check import ServiceCheckMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.add_middleware(ServiceCheckMiddleware)

# MongoDB setup
try:
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = MongoClient(mongodb_url)
    db = client.code_review_db
    # Test the connection
    client.server_info()
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Models
class ReviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class CodeReview(BaseModel):
    id: str
    title: str
    description: str
    code_snippet: str
    author_id: str
    reviewer_id: Optional[str] = None
    status: ReviewStatus = ReviewStatus.PENDING
    comments: List[str] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class User(BaseModel):
    username: str
    email: str
    role: str  # "developer" or "reviewer"

# Service URLs
CALENDAR_SERVICE_URL = os.getenv("CALENDAR_SERVICE_URL", "http://calendar-service:5000")
FORUM_SERVICE_URL = os.getenv("FORUM_SERVICE_URL", "http://forum-service:8004")

# Add calendar service integration
async def create_calendar_event(review_data: dict):
    try:
        calendar_service_url = f"{CALENDAR_SERVICE_URL}/api/events/code-review"
        response = requests.post(calendar_service_url, json=review_data)
        return response.json()
    except Exception as e:
        print(f"Failed to create calendar event: {e}")
        return None

# Add forum service integration
async def create_forum_topic_for_review(review_data: dict):
    try:
        # Prepare forum topic data
        topic_data = {
            "title": f"Code Review: {review_data['title']}",
            "description": f"Discussion for code review: {review_data['description']}",
            "is_scheduled": 0  # Not scheduled by default
        }

        # Send request to forum service
        response = requests.post(f"{FORUM_SERVICE_URL}/topics/", json=topic_data)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to create forum topic: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating forum topic: {str(e)}")
        return None

# Routes
@app.post("/reviews/", response_model=CodeReview)
async def create_review(review: CodeReview):
    try:
        # Convert Pydantic model to dict (handle both old and new Pydantic versions)
        review_dict = review.dict() if hasattr(review, 'dict') else review.model_dump()
        
        # Insert into MongoDB
        try:
            result = db.reviews.insert_one(review_dict)
            logger.info(f"Successfully created review with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Failed to insert review into MongoDB: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create review in database")

        # Create calendar event (non-blocking)
        try:
            calendar_event = await create_calendar_event({
                "review_id": review_dict["id"],
                "title": review_dict["title"],
                "description": review_dict["description"],
                "status": review_dict["status"]
            })
            if not calendar_event:
                logger.warning("Failed to create calendar event")
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            calendar_event = None

        # Create forum topic (non-blocking)
        try:
            forum_topic = await create_forum_topic_for_review({
                "title": review_dict["title"],
                "description": review_dict["description"]
            })
            if not forum_topic:
                logger.warning("Failed to create forum topic")
        except Exception as e:
            logger.error(f"Error creating forum topic: {str(e)}")
            forum_topic = None

        return {**review_dict, "calendar_event": calendar_event, "forum_topic": forum_topic}
    except Exception as e:
        logger.error(f"Unexpected error in create_review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/reviews/", response_model=List[CodeReview])
async def get_reviews(status: Optional[ReviewStatus] = None):
    query = {} if status is None else {"status": status}
    reviews = list(db.reviews.find(query))
    return reviews

@app.get("/reviews/{review_id}", response_model=CodeReview)
async def get_review(review_id: str):
    review = db.reviews.find_one({"id": review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@app.put("/reviews/{review_id}")
async def update_review(review_id: str, review: CodeReview):
    try:
        # Verify the review exists
        existing_review = db.reviews.find_one({"id": review_id})
        if not existing_review:
            raise HTTPException(status_code=404, detail="Review not found")

        # Update the review
        review_dict = review.dict()
        result = db.reviews.update_one(
            {"id": review_id},
            {"$set": review_dict}
        )
        
        if result.modified_count > 0:
            return {"message": "Review updated successfully"}
        return {"message": "No changes were made to the review"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")

@app.delete("/reviews/{review_id}")
async def delete_review(review_id: str):
    result = db.reviews.delete_one({"id": review_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}

@app.post("/users/")
async def create_user(user: User):
    try:
        # Check if user already exists
        existing_user = db.users.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Create new user
        user_dict = user.dict()
        result = db.users.insert_one(user_dict)
        
        if result.inserted_id:
            return {"message": "User created successfully"}
        return {"message": "User creation failed"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get("/users/", response_model=List[User])
async def get_users(role: Optional[str] = None):
    query = {} if role is None else {"role": role}
    users = list(db.users.find(query))
    return users

@app.get("/users/{username}", response_model=User)
async def get_user(username: str):
    user = db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{username}", response_model=User)
async def update_user(username: str, user: User):
    # Check if user exists
    existing_user = db.users.find_one({"username": username})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = user.model_dump()
    db.users.update_one(
        {"username": username},
        {"$set": user_dict}
    )
    return user_dict

@app.delete("/users/{username}")
async def delete_user(username: str):
    result = db.users.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint for the service."""
    return {"status": "healthy"}

@app.get("/services/status")
async def check_services():
    """Check the status of all dependent services."""
    status = await service_health.check_all_services()
    return status

