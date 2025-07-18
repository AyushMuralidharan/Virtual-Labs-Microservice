# Microservices Integration Platform

This project integrates multiple microservices to create a comprehensive software development and project management platform. The services include Bug Tracking, Calendar Management, Code Review, Forum, Architectural Modeling, and Version Control.

## Services Overview

### Bug Tracker Service
- **Port**: 8000
- **API Base URL**: `http://localhost:8000`
- Built with FastAPI and MongoDB
- Handles bug creation, assignment, and status updates
- Integrates with Calendar and Forum services

### Code Review Service
- **Port**: 8001
- **API Base URL**: `http://localhost:8001`
- Built with FastAPI and MongoDB
- Manages code review requests and feedback
- Integrates with Calendar and Version Control services

### Forum Service
- **Port**: 8004
- **API Base URL**: `http://localhost:8004`
- Built with FastAPI and PostgreSQL
- Handles discussions, comments, and knowledge sharing
- Integrates with Calendar and Bug Tracker services

### Calendar Service
- **Port**: 5000
- **API Base URL**: `http://localhost:5000`
- Built with Express.js and MongoDB
- Manages events and integrates with all other services
- Provides a unified calendar view for all activities

### Calendar Client (Frontend)
- **Port**: 3000
- **URL**: `http://localhost:3000`
- Built with React
- Provides a user-friendly interface for calendar management

### Architectural Model Service
- **Port**: 8003
- **API Base URL**: `http://localhost:8003`
- Built with FastAPI and MongoDB
- Handles architectural visualization and documentation
- Integrates with Calendar service

### Version Control Service
- **Port**: 8002
- **API Base URL**: `http://localhost:8002`
- Built with FastAPI and MongoDB
- Manages code repositories and version history
- Integrates with Calendar and Code Review services

## Database Services
- **MongoDB**: `localhost:27017` (Used by most services)
- **PostgreSQL**: `localhost:5432` (Used by Forum service)

## Features

### Integrated Services
1. **Bug Tracking + Calendar Integration**
   - Automatic calendar event creation for new bugs
   - Real-time status updates in calendar
   - Priority-based event categorization

2. **Code Review + Calendar Integration**
   - Scheduled code review events
   - Review deadline tracking
   - Integration with version control

3. **Forum + Calendar Integration**
   - Discussion thread events
   - Meeting scheduling
   - Knowledge sharing sessions

4. **Architectural Model + Calendar Integration**
   - Architecture review meetings
   - Documentation updates
   - Team collaboration sessions

5. **Version Control + Calendar Integration**
   - Commit history tracking
   - Release planning
   - Code freeze events

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd Microservices
```

2. Start all services using Docker Compose:
```bash
docker-compose up --build
```

This will start all services and their dependencies:
- Bug Tracker (port 8000)
- Code Review (port 8001)
- Forum Service (port 8004)
- Calendar Service (port 5000)
- Calendar Client (port 3000)
- Architectural Model (port 8003)
- Version Control (port 8002)
- MongoDB (port 27017)
- PostgreSQL (port 5432)

## Accessing Services

All services can be accessed through their respective URLs:
- Calendar Interface: `http://localhost:3000`
- Bug Tracker API: `http://localhost:8000`
- Code Review API: `http://localhost:8001`
- Forum API: `http://localhost:8004`
- Calendar API: `http://localhost:5000`
- Architectural Model API: `http://localhost:8003`
- Version Control API: `http://localhost:8002`

## Environment Variables

### Common Variables
- `MONGODB_URL`: MongoDB connection string
- `CALENDAR_SERVICE_URL`: URL of the calendar service

### Service-Specific Variables
- Forum Service: `DATABASE_URL` (PostgreSQL connection)
- Version Control: `REPOS_DIR` (Repository directory)
- Architectural Model: `PYTHONUNBUFFERED=1`

## Development

### Adding New Features
1. Update the respective service's code
2. Add new API endpoints if needed
3. Update the integration logic in related services
4. Test the changes locally
5. Update the documentation

### Testing
1. Start all services using docker-compose
2. Use the provided API endpoints to test functionality
3. Verify service integrations are working correctly
4. Check the calendar interface for visual confirmation

## Troubleshooting

### Common Issues

1. **Service Communication Issues**
   - Verify all services are running
   - Check environment variables
   - Ensure correct port mappings

2. **Database Connection Issues**
   - Verify MongoDB and PostgreSQL are running
   - Check connection strings
   - Ensure proper network configuration

3. **API Endpoint Issues**
   - Verify correct endpoint URLs
   - Check request/response formats
   - Ensure proper authentication if required

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
