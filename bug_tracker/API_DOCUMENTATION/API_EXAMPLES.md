# Bug Tracker Microservice - API Examples

## Client Operations

### Create a Bug Report
```bash
curl -X POST http://localhost:8000/client/bugs/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Login button not working",
    "description": "The login button on the homepage does not respond when clicked"
  }'
```

## Manager Operations

### Create a Client
```bash
curl -X POST http://localhost:8000/manager/client/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation"
  }'
```

### Create an Employee
```bash
curl -X POST http://localhost:8000/manager/employee/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe"
  }'
```

### List All Employees
```bash
curl -X GET http://localhost:8000/manager/employees
```

### List All Clients
```bash
curl -X GET http://localhost:8000/manager/clients
```

### Assign Bug to Employee
```bash
curl -X POST http://localhost:8000/manager/bugs/assign \
  -H "Content-Type: application/json" \
  -d '{
    "bug_id": "123",
    "employee_id": "456"
  }'
```

### List All Bugs
```bash
curl -X GET http://localhost:8000/manager/bugs
```

## Employee Operations

### Get Employee's Bugs
```bash
curl -X GET http://localhost:8000/employee/456/bugs
```

### Get Completed Bugs
```bash
curl -X GET http://localhost:8000/employee/456/bugs/completed
```

### Get Pending Bugs
```bash
curl -X GET http://localhost:8000/employee/456/bugs/pending
```

### Update Bug Status
```bash
curl -X POST http://localhost:8000/employee/456/bugs/update \
  -H "Content-Type: application/json" \
  -d '{
    "bug_id": "123",
    "status": "completed"
  }'
```

## Example Responses

### Successful Bug Creation
```json
{
  "status": "success",
  "data": {
    "bug_id": "123",
    "title": "Login button not working",
    "description": "The login button on the homepage does not respond when clicked",
    "status": "pending",
    "employee_id": null
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Employee not found",
  "details": {
    "employee_id": "456"
  }
} 