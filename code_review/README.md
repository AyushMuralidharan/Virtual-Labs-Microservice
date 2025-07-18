# Code Review Microservice

A FastAPI-based microservice for managing code reviews and users in a development environment.

## Features

- User Management (Create, Read, Update, Delete)
- Code Review Management (Create, Read, Update, Delete)
- Role-based user system (developer/reviewer)
- Review status tracking (pending, in_progress, completed, rejected)
- Comment system for reviews

## Prerequisites

- Python 3.8+
- MongoDB
- Docker (optional)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export MONGODB_URL="mongodb://localhost:27017"  # or your MongoDB connection string
```

## Running the Service

### Local Development
```bash
uvicorn main:app --reload
```

### Using Docker
```bash
docker build -t code-review-service .
docker run -p 8000:8000 code-review-service
```

## API Documentation

Once the service is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Users

#### Create User
```http
POST /users/
```
Request body:
```json
{
    "id": "user123",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "developer"
}
```

#### Get All Users
```http
GET /users/
```
Optional query parameter: `role` (filter by role)

#### Get User by ID
```http
GET /users/{user_id}
```

#### Update User
```http
PUT /users/{user_id}
```
Request body: Same as create user

#### Delete User
```http
DELETE /users/{user_id}
```

### Code Reviews

#### Create Review
```http
POST /reviews/
```
Request body:
```json
{
    "id": "review123",
    "title": "Feature Implementation",
    "description": "Review the new authentication system",
    "code_snippet": "def authenticate(): ...",
    "author_id": "user123",
    "reviewer_id": "user456",
    "status": "pending"
}
```

#### Get All Reviews
```http
GET /reviews/
```
Optional query parameter: `status` (filter by status)

#### Get Review by ID
```http
GET /reviews/{review_id}
```

#### Update Review
```http
PUT /reviews/{review_id}
```
Request body: Same as create review

#### Delete Review
```http
DELETE /reviews/{review_id}
```

## Data Models

### User
```python
class User(BaseModel):
    id: str
    username: str
    email: str
    role: str  # "developer" or "reviewer"
    created_at: datetime
```

### Code Review
```python
class CodeReview(BaseModel):
    id: str
    title: str
    description: str
    code_snippet: str
    author_id: str
    reviewer_id: Optional[str]
    status: ReviewStatus  # pending, in_progress, completed, rejected
    comments: List[str]
    created_at: datetime
    updated_at: datetime
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400: Bad Request (e.g., duplicate ID, invalid data)
- 404: Not Found (e.g., resource doesn't exist)
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 