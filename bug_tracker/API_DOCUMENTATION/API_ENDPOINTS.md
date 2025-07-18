# Bug Tracker Microservice - API Endpoints

## Client Endpoints

### Create a Bug Report
- **URL**: `/client/bugs/create`
- **Method**: `POST`
- **Description**: Submit a new bug report
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string"
  }
  ```
- **Response**: Created bug object

## Manager Endpoints

### Create a Client
- **URL**: `/manager/client/create`
- **Method**: `POST`
- **Description**: Create a new client
- **Request Body**:
  ```json
  {
    "name": "string"
  }
  ```
- **Response**: Created client object

### Create an Employee
- **URL**: `/manager/employee/create`
- **Method**: `POST`
- **Description**: Create a new employee
- **Request Body**:
  ```json
  {
    "name": "string"
  }
  ```
- **Response**: Created employee object

### List All Employees
- **URL**: `/manager/employees`
- **Method**: `GET`
- **Description**: Get a list of all employees
- **Response**: Array of employee objects

### List All Clients
- **URL**: `/manager/clients`
- **Method**: `GET`
- **Description**: Get a list of all clients
- **Response**: Array of client objects

### Assign Bug to Employee
- **URL**: `/manager/bugs/assign`
- **Method**: `POST`
- **Description**: Assign a bug to an employee
- **Request Body**:
  ```json
  {
    "bug_id": "string",
    "employee_id": "string"
  }
  ```
- **Response**: Updated bug object

### List All Bugs
- **URL**: `/manager/bugs`
- **Method**: `GET`
- **Description**: Get a list of all bugs
- **Response**: Array of bug objects

## Employee Endpoints

### Get Employee's Bugs
- **URL**: `/employee/{employee_id}/bugs`
- **Method**: `GET`
- **Description**: Get all bugs assigned to an employee
- **Response**: Array of bug objects

### Get Completed Bugs
- **URL**: `/employee/{employee_id}/bugs/completed`
- **Method**: `GET`
- **Description**: Get all completed bugs for an employee
- **Response**: Array of bug objects

### Get Pending Bugs
- **URL**: `/employee/{employee_id}/bugs/pending`
- **Method**: `GET`
- **Description**: Get all pending bugs for an employee
- **Response**: Array of bug objects

### Update Bug Status
- **URL**: `/employee/{employee_id}/bugs/update`
- **Method**: `POST`
- **Description**: Update the status of a bug
- **Request Body**:
  ```json
  {
    "bug_id": "string",
    "status": "string"
  }
  ```
- **Response**: Updated bug object 