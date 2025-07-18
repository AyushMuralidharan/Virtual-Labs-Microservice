# Architectural Model Converter Microservice

A microservice that converts Python code into various architectural models including UML, 4+1, and ADL representations.

## Features

- Convert Python code to UML class diagrams
- Generate 4+1 architectural views
- Create Architecture Description Language (ADL) representations
- RESTful API interface
- Swagger UI documentation
- Docker containerization support

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ (for local development)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd architectural_model
```

2. Build and start the container:
```bash
docker-compose up --build
```

3. Access the API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### 1. Upload and Visualize Code
```
POST /visualize/upload
```
Parameters:
- `file`: Python code file to upload
- `model_type`: Type of visualization (uml, 4+1, or adl)

### 2. View Visualization
```
GET /visualize/{model_type}?code_hash={hash}
```
Parameters:
- `model_type`: Type of visualization (uml, 4+1, or adl)
- `code_hash`: Hash returned from upload endpoint

## Model Types

1. **UML (uml)**
   - Generates class diagrams
   - Shows inheritance relationships
   - Displays class attributes and methods

2. **4+1 (4+1)**
   - Logical view
   - Process view
   - Development view
   - Physical view
   - Scenarios

3. **ADL (adl)**
   - Formal architectural description
   - Component and connector specifications
   - Interface definitions

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

## Project Structure

```
architectural_model/
├── main.py              # FastAPI application
├── code_analyzer.py     # Code analysis logic
├── visualizer.py        # Visualization generation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── temp_visualizations/ # Temporary storage for visualizations
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Support

For support, please open an issue in the GitHub repository. 