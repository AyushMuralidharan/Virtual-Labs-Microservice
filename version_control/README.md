# Version Control Microservice

A microservice implementing version control functionality using Python FastAPI and Docker.

## Features

- Create and manage Git repositories
- Create and switch between branches
- Commit changes to files
- View commit history and diffs
- Merge branches
- RESTful API for all operations

## Requirements

- Docker
- Docker Compose

## Getting Started

1. Clone this repository
2. Build and run the Docker container:

```bash
docker-compose up -d
```

3. Access the API documentation at http://localhost:8000/docs

## API Endpoints

The microservice provides the following endpoints:

- `GET /` - Check if the service is running
- `GET /repos` - List all repositories
- `POST /repos/{repo_name}` - Create a new repository
- `DELETE /repos/{repo_name}` - Delete a repository
- `GET /repos/{repo_name}/branches` - List all branches in a repository
- `POST /repos/{repo_name}/branches` - Create a new branch
- `GET /repos/{repo_name}/commits` - List commits in a repository
- `GET /repos/{repo_name}/files` - List files in a repository branch
- `GET /repos/{repo_name}/files/{file_path}` - Get the content of a file
- `PUT /repos/{repo_name}/files/{file_path}` - Update a file and commit the changes
- `DELETE /repos/{repo_name}/files/{file_path}` - Delete a file and commit the changes
- `POST /repos/{repo_name}/checkout` - Checkout a branch
- `GET /repos/{repo_name}/diff` - Get the diff between two commits
- `POST /repos/{repo_name}/merge` - Merge a source branch into a target branch



