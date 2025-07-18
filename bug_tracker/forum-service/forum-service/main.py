from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import requests

app = FastAPI()

# Calendar service URL
CALENDAR_SERVICE_URL = os.getenv("CALENDAR_SERVICE_URL", "http://localhost:5000")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/content_management")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Database models
    class TopicDB(Base):
        __tablename__ = "topics"
        id = Column(String, primary_key=True)
        title = Column(String, nullable=False)
        description = Column(Text, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        # New fields for date-specific topics
        scheduled_date = Column(DateTime, nullable=True)
        end_date = Column(DateTime, nullable=True)
        is_scheduled = Column(Integer, default=0)  # 0: not scheduled, 1: scheduled
        calendar_event_id = Column(String, nullable=True)  # Reference to calendar event
        posts = relationship("PostDB", back_populates="topic", cascade="all, delete-orphan")

    class PostDB(Base):
        __tablename__ = "posts"
        id = Column(String, primary_key=True)
        topic_id = Column(String, ForeignKey("topics.id"))
        content = Column(Text, nullable=False)
        author = Column(String, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        topic = relationship("TopicDB", back_populates="posts")

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Successfully connected to the database and created tables")
except Exception as e:
    print(f"Error connecting to the database: {e}")

# Pydantic models
class TopicBase(BaseModel):
    title: str
    description: str
    scheduled_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_scheduled: int = 0
    calendar_event_id: Optional[str] = None

class PostBase(BaseModel):
    content: str
    author: str

class PostResponse(PostBase):
    id: str
    topic_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class TopicResponse(TopicBase):
    id: str
    created_at: datetime
    scheduled_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_scheduled: int = 0
    calendar_event_id: Optional[str] = None
    posts: List[PostResponse] = []

    class Config:
        orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create calendar event for a forum topic
async def create_calendar_event_for_topic(topic_data):
    """Create a calendar event for a forum topic"""
    try:
        # Prepare event data
        event_data = {
            "title": f"Forum Topic: {topic_data.title}",
            "start": topic_data.scheduled_date.isoformat() if topic_data.scheduled_date else datetime.now().isoformat(),
            "end": topic_data.end_date.isoformat() if topic_data.end_date else (datetime.now() + timedelta(days=1)).isoformat(),
            "desc": topic_data.description,
            "allDay": False,
            "createdBy": "forum_service",
            "eventType": "forum_topic",
            "referenceId": topic_data.id,
            "status": "active"
        }

        # Print debug information
        print(f"Sending request to calendar service: {CALENDAR_SERVICE_URL}/api/events/forum-topic")
        print(f"Event data: {event_data}")

        # Send request to calendar service
        response = requests.post(f"{CALENDAR_SERVICE_URL}/api/events/forum-topic", json=event_data)

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code in [200, 201]:
            print(f"Calendar event created for topic {topic_data.id}")
            event_id = response.json().get('_id')
            print(f"Event ID: {event_id}")
            return event_id
        else:
            print(f"Failed to create calendar event: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating calendar event: {str(e)}")
        return None

# Create topic
@app.post("/topics/", response_model=TopicResponse)
async def create_topic(topic: TopicBase, db: Session = Depends(get_db)):
    # Print debug information
    print(f"Creating topic: {topic.title}")
    print(f"Scheduled date: {topic.scheduled_date}")
    print(f"End date: {topic.end_date}")
    print(f"Is scheduled: {topic.is_scheduled}")

    # Set is_scheduled flag if scheduled_date is provided but is_scheduled is not set
    if topic.scheduled_date and topic.is_scheduled == 0:
        topic.is_scheduled = 1
        print("Setting is_scheduled to 1 because scheduled_date is provided")

    # Create a new topic with all fields
    db_topic = TopicDB(
        id=os.urandom(8).hex(),
        title=topic.title,
        description=topic.description,
        scheduled_date=topic.scheduled_date,
        end_date=topic.end_date,
        is_scheduled=topic.is_scheduled
    )

    # Add to database
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)

    print(f"Topic created with ID: {db_topic.id}")
    print(f"Is scheduled flag: {db_topic.is_scheduled}")

    # Always create a calendar event for the topic
    calendar_event_id = await create_calendar_event_for_topic(db_topic)
    if calendar_event_id:
        # Update the topic with the calendar event ID
        db_topic.calendar_event_id = calendar_event_id
        db.commit()
        db.refresh(db_topic)
        print(f"Updated topic with calendar event ID: {calendar_event_id}")

    return db_topic

# Get all topics
@app.get("/topics/", response_model=List[TopicResponse])
async def get_all_topics(db: Session = Depends(get_db)):
    topics = db.query(TopicDB).all()
    return topics

# Get topic by ID
@app.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str, db: Session = Depends(get_db)):
    topic = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

# Update topic
@app.put("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(topic_id: str, topic: TopicBase, db: Session = Depends(get_db)):
    db_topic = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Update basic fields
    db_topic.title = topic.title
    db_topic.description = topic.description
    db_topic.scheduled_date = topic.scheduled_date
    db_topic.end_date = topic.end_date
    db_topic.is_scheduled = topic.is_scheduled

    # Handle calendar event updates
    if topic.is_scheduled == 1 and topic.scheduled_date:
        if db_topic.calendar_event_id:
            # Update existing calendar event
            try:
                event_data = {
                    "title": f"Forum Topic: {topic.title}",
                    "start": topic.scheduled_date.isoformat(),
                    "end": topic.end_date.isoformat() if topic.end_date else (topic.scheduled_date + timedelta(days=1)).isoformat(),
                    "desc": topic.description
                }

                response = requests.put(
                    f"{CALENDAR_SERVICE_URL}/api/events/by-reference/{db_topic.id}",
                    json=event_data
                )

                if response.status_code != 200:
                    print(f"Failed to update calendar event: {response.text}")
            except Exception as e:
                print(f"Error updating calendar event: {str(e)}")
        else:
            # Create new calendar event
            calendar_event_id = await create_calendar_event_for_topic(db_topic)
            if calendar_event_id:
                db_topic.calendar_event_id = calendar_event_id
    elif db_topic.calendar_event_id:
        # Topic is no longer scheduled but has a calendar event - delete it
        try:
            response = requests.delete(f"{CALENDAR_SERVICE_URL}/api/events/{db_topic.calendar_event_id}")
            if response.status_code == 200:
                db_topic.calendar_event_id = None
        except Exception as e:
            print(f"Error deleting calendar event: {str(e)}")

    db.commit()
    db.refresh(db_topic)
    return db_topic

# Delete topic
@app.delete("/topics/{topic_id}")
async def delete_topic(topic_id: str, db: Session = Depends(get_db)):
    db_topic = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Delete associated calendar event if it exists
    try:
        print(f"Attempting to delete calendar event for topic {db_topic.id}")
        response = requests.delete(f"{CALENDAR_SERVICE_URL}/api/events/by-reference/{db_topic.id}")
        print(f"Delete response status: {response.status_code}")
        print(f"Delete response content: {response.text}")

        if response.status_code not in [200, 204]:
            print(f"Failed to delete calendar event: {response.text}")
    except Exception as e:
        print(f"Error deleting calendar event: {str(e)}")

    # Delete the topic from the database
    db.delete(db_topic)
    db.commit()
    return {"status": "deleted", "id": topic_id}

# Create post in topic
@app.post("/topics/{topic_id}/posts/", response_model=PostResponse)
async def create_post(topic_id: str, post: PostBase, db: Session = Depends(get_db)):
    topic = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    db_post = PostDB(
        id=os.urandom(8).hex(),
        topic_id=topic_id,
        content=post.content,
        author=post.author
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Get all posts in topic
@app.get("/topics/{topic_id}/posts/", response_model=List[PostResponse])
async def get_topic_posts(topic_id: str, db: Session = Depends(get_db)):
    topic = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic.posts