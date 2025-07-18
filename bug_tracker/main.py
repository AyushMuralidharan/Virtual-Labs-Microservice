from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pymongo import MongoClient
from typing import Optional, Dict
from bson import ObjectId
import uvicorn
import os
import requests
from datetime import datetime, timedelta
from bug_tracker.utils.service_health import service_health
from bug_tracker.middleware.service_check import ServiceCheckMiddleware

app = FastAPI()

# Add middleware
app.add_middleware(ServiceCheckMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# MongoDB setup
mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = MongoClient(mongodb_url)
db = client["bugtracker_db"]  # Use a specific DB

# Service URLs
CALENDAR_SERVICE_URL = os.getenv("CALENDAR_SERVICE_URL", "http://localhost:5000")
FORUM_SERVICE_URL = os.getenv("FORUM_SERVICE_URL", "http://localhost:8004")

# Service status tracking
service_status: Dict[str, bool] = {
    "calendar": True,
    "forum": True
}

# Helper to get service URL
def get_service_url(service_name: str, default_url: str) -> str:
    env_url = os.getenv(f"{service_name.upper()}_SERVICE_URL", default_url)
    print(f"Using {service_name} service URL: {env_url}")
    return env_url

# Helper to check service availability
async def check_service_availability(service_name: str, service_url: str) -> bool:
    try:
        if service_name == "calendar":
            # For calendar service, check the root endpoint
            url = f"{service_url}/api"
            print(f"Checking calendar service at: {url}")
            response = requests.get(url, timeout=5)
            print(f"Calendar service check - Status: {response.status_code}, URL: {url}")
            return response.status_code == 200
        else:
            # For other services, check their health endpoints
            response = requests.get(f"{service_url}/health", timeout=5)
            return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        print(f"Error checking {service_name} service availability: {str(e)}")
        return False

# Helper to get service status message
def get_service_status_message() -> str:
    unavailable_services = [service for service, status in service_status.items() if not status]
    if unavailable_services:
        return f"The following services are currently unavailable: {', '.join(unavailable_services)}"
    return "All services are available"

employee_collection = db["employee_collection"]
bug_collection = db["bug_collection"]
manager_collection = db["manager_collection"]
client_collection = db["client_collection"]

# Helper to serialize ObjectId
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Pydantic models
class Employee(BaseModel):
    employee_id: str
    name: str
    bugs_completed: int = 0
    bugs_pending: int = 0

class Bug(BaseModel):
    bug_id: str = Field(..., min_length=1, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    status: str = Field(default="Pending", pattern="^(Pending|In Progress|Completed)$")

class Manager(BaseModel):
    manager_id: str
    name: str

class Client(BaseModel):
    client_id: str
    name: str

# Routes

@app.get("/")
async def root():
    return {"message": "Welcome to the Bug Tracker"}

@app.get("/health")
async def health_check():
    """Health check endpoint for the service."""
    return {"status": "healthy"}

@app.get("/services/status")
async def check_services():
    """Check the status of all dependent services."""
    status = await service_health.check_all_services()
    return status

# --------------------- CLIENT ---------------------

async def create_calendar_event_for_bug(bug: Bug):
    """Create a calendar event for a new bug"""
    calendar_url = get_service_url("calendar", "http://localhost:5000")
    print(f"Checking calendar service at {calendar_url}")
    service_status["calendar"] = await check_service_availability("calendar", calendar_url)
    
    if not service_status["calendar"]:
        print("Calendar service is marked as unavailable")
        raise HTTPException(status_code=503, detail="Calendar service is currently unavailable")

    event_data = {
        "title": f"Bug: {bug.title}",
        "start": datetime.now().isoformat(),
        "end": (datetime.now() + timedelta(days=7)).isoformat(),  # Default 7-day deadline
        "desc": bug.description,
        "allDay": False,
        "createdBy": "bug_tracker",
        "eventType": "bug",
        "referenceId": bug.bug_id,
        "status": bug.status,
        "priority": "high"  # Default priority for bugs
    }

    print(f"Attempting to create calendar event at {calendar_url}/api/events")
    print(f"Event data: {event_data}")

    try:
        response = requests.post(
            f"{calendar_url}/api/events",
            json=event_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Calendar service response status: {response.status_code}")
        print(f"Calendar service response text: {response.text}")
        
        # Any 2xx status code is considered successful
        if 200 <= response.status_code < 300:
            print(f"Calendar event created for bug {bug.bug_id}")
            return response.json()
        else:
            print(f"Failed to create calendar event: {response.text}")
            service_status["calendar"] = False
            raise HTTPException(status_code=503, detail=f"Failed to create calendar event: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception while creating calendar event: {str(e)}")
        service_status["calendar"] = False
        raise HTTPException(status_code=503, detail=f"Failed to create calendar event: {str(e)}")
    except Exception as e:
        print(f"Unexpected exception while creating calendar event: {str(e)}")
        service_status["calendar"] = False
        raise HTTPException(status_code=503, detail=f"Failed to create calendar event: {str(e)}")

@app.post("/client/bugs/create")
async def create_bug(bug: Bug):
    # Check service availability before proceeding
    service_status["calendar"] = await check_service_availability("calendar", CALENDAR_SERVICE_URL)
    service_status["forum"] = await check_service_availability("forum", FORUM_SERVICE_URL)
    
    # Insert bug into database
    bug_collection.insert_one(bug.dict())
    if not bug_collection.find_one({"bug_id": bug.bug_id}):
        return {"message": "Bug creation failed"}
    
    # Try to create calendar event
    try:
        calendar_event = await create_calendar_event_for_bug(bug)
        if calendar_event:  # If we got a response back, it was successful
            return {
                "message": "Bug created successfully with calendar event",
                "service_status": service_status,
                "calendar_event": calendar_event
            }
    except HTTPException as e:
        return {
            "message": "Bug created but calendar integration failed",
            "error": e.detail,
            "service_status": service_status
        }
    
    return {
        "message": "Bug created successfully",
        "service_status": service_status
    }

# --------------------- MANAGER ---------------------

@app.post("/manager/client/create")
async def create_client(client_data: Client):
    try:
        # Check if client already exists
        if client_collection.find_one({"client_id": client_data.client_id}):
            return {"message": "Client already exists"}
        
        # Convert Pydantic model to dict and insert
        client_dict = client_data.dict()
        result = client_collection.insert_one(client_dict)
        
        # Verify insertion
        if result.inserted_id:
            return {"message": "Client created successfully"}
        else:
            return {"message": "Client creation failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating client: {str(e)}")

@app.post("/manager/employee/create")
async def create_employee(employee: Employee):
    try:
        # Check if employee already exists
        if employee_collection.find_one({"employee_id": employee.employee_id}):
            return {"message": "Employee already exists"}
        
        # Convert Pydantic model to dict and insert
        employee_dict = employee.dict()
        result = employee_collection.insert_one(employee_dict)
        
        # Verify insertion
        if result.inserted_id:
            return {"message": "Employee created successfully"}
        else:
            return {"message": "Employee creation failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating employee: {str(e)}")

@app.get("/manager/employees")
async def list_employees():
    return [serialize_doc(emp) for emp in employee_collection.find()]


@app.get("/manager/clients")
async def list_clients():
    return [serialize_doc(client) for client in client_collection.find()]

@app.post("/manager/bugs/assign")
async def assign_bug(bug_id: str, employee_id: str):
    if bug_collection.find_one({"bug_id": bug_id}):
        bug_collection.update_one(
            {"bug_id": bug_id},
            {"$set": {"employee_id": employee_id}}
        )
        employee_collection.update_one(
            {"employee_id": employee_id},
            {"$inc": {"bugs_pending": 1}}
        )
        return {"message": "Bug assigned successfully"}
    return {"message": "Bug assignment failed"}


@app.get("/manager/bugs")
async def list_bugs():
    return [serialize_doc(bug) for bug in bug_collection.find()]

# --------------------- EMPLOYEE ---------------------

@app.get("/employee/{employee_id}/bugs")
async def list_employee_bugs(employee_id: str):
    return [serialize_doc(bug) for bug in bug_collection.find({"employee_id": employee_id})]

@app.get("/employee/{employee_id}/bugs/completed")
async def list_completed_bugs(employee_id: str):
    return [serialize_doc(bug) for bug in bug_collection.find({"employee_id": employee_id, "status": "Completed"})]

@app.get("/employee/{employee_id}/bugs/pending")
async def list_pending_bugs(employee_id: str):
    return [serialize_doc(bug) for bug in bug_collection.find({"employee_id": employee_id, "status": "Pending"})]

@app.post("/employee/{employee_id}/bugs/update")
async def update_bug_status(employee_id: str, bug_id: str, status: str):
    bug = bug_collection.find_one({"bug_id": bug_id})
    if bug:
        bug_collection.update_one(
            {"bug_id": bug_id, "employee_id": employee_id},
            {"$set": {"status": status}}
        )
        employee_collection.update_one(
            {"employee_id": employee_id},
            {"$inc": {"bugs_completed": 1}}
        )

        # Update calendar event status
        try:
            response = requests.put(
                f"{CALENDAR_SERVICE_URL}/api/events/by-reference/{bug_id}",
                json={"status": status}
            )
            if response.status_code != 200:
                print(f"Failed to update calendar event status: {response.text}")
        except Exception as e:
            print(f"Error updating calendar event status: {str(e)}")

        return {"message": f"Bug {bug_id} updated to status {status}"}
    return {"message": "Bug not found"}

# --------------------- FORUM INTEGRATION ---------------------

@app.post("/bugs/{bug_id}/create-forum-topic")
async def create_forum_topic_for_bug(bug_id: str, title: str, description: str):
    """Create a forum topic for discussion about a specific bug"""
    bug = bug_collection.find_one({"bug_id": bug_id})
    if not bug:
        return {"message": "Bug not found"}

    try:
        # Prepare forum topic data
        topic_data = {
            "title": title or f"Discussion: Bug #{bug_id} - {bug['title']}",
            "description": description or f"This topic is for discussing bug #{bug_id}: {bug['description']}",
            "is_scheduled": 0  # Not scheduled by default
        }

        # Send request to forum service
        response = requests.post(f"{FORUM_SERVICE_URL}/topics/", json=topic_data)

        if response.status_code == 200:
            return {"message": "Forum topic created successfully", "topic": response.json()}
        else:
            return {"message": f"Failed to create forum topic: {response.text}"}
    except Exception as e:
        return {"message": f"Error creating forum topic: {str(e)}"}

# --------------------- MAIN ---------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
