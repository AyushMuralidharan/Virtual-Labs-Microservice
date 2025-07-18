# Bug Tracker Microservice - Data Models

## Bug Model
```json
{
  "bug_id": "string",
  "title": "string",
  "description": "string",
  "status": "string",
  "employee_id": "string (optional)"
}
```

### Fields Description
- `bug_id`: Unique identifier for the bug
- `title`: Short description of the bug
- `description`: Detailed explanation of the bug
- `status`: Current status of the bug (e.g., "pending", "in_progress", "completed")
- `employee_id`: ID of the employee assigned to the bug (optional)

## Employee Model
```json
{
  "employee_id": "string",
  "name": "string",
  "bugs_completed": "integer",
  "bugs_pending": "integer"
}
```

### Fields Description
- `employee_id`: Unique identifier for the employee
- `name`: Full name of the employee
- `bugs_completed`: Number of bugs completed by the employee
- `bugs_pending`: Number of bugs currently assigned to the employee

## Client Model
```json
{
  "client_id": "string",
  "name": "string"
}
```

### Fields Description
- `client_id`: Unique identifier for the client
- `name`: Name of the client or organization

## Response Models

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data object
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "string",
  "details": {
    // Additional error details (optional)
  }
}
``` 