# Bug Tracker Microservice

A FastAPI-based microservice for tracking bugs, managing employees, and handling client requests in a software development environment.

## Features

- **Client Management**
  - Create and manage clients
  - Submit bug reports

- **Manager Features**
  - Create and manage employees
  - Create and manage clients
  - Assign bugs to employees
  - View all bugs and their status
  - Track employee performance

- **Employee Features**
  - View assigned bugs
  - Update bug status
  - Track completed and pending bugs

## Prerequisites

- Docker and Docker Compose
- Python 3.9 or higher (for local development)
- MongoDB (handled automatically with Docker Compose)

## Project Structure

```
bug_tracker/
├── main.py              # FastAPI application and routes
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── API_DOCUMENTATION/  # API documentation
    ├── API_OVERVIEW.md
    ├── API_ENDPOINTS.md
    ├── API_MODELS.md
    └── API_EXAMPLES.md
```

## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd bug_tracker
   ```
3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

The service will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MongoDB: mongodb://localhost:27017

### Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start MongoDB (if not using Docker)

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Detailed API documentation is available in the `API_DOCUMENTATION` directory:
- `API_OVERVIEW.md`: General information
- `API_ENDPOINTS.md`: All available endpoints
- `API_MODELS.md`: Data models
- `API_EXAMPLES.md`: Usage examples

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document all functions and classes

## Troubleshooting

1. **MongoDB Connection Issues**
   - Ensure MongoDB is running
   - Check connection string in environment variables
   - Verify MongoDB port (default: 27017)

2. **API Not Accessible**
   - Check if containers are running: `docker ps`
   - Verify port mappings in docker-compose.yml
   - Check logs: `docker-compose logs`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository. 