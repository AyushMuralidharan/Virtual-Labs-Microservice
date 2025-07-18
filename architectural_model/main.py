from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from typing import Optional, Dict, Any, Union
from code_analyzer import CodeAnalyzer, UMLGenerator, FourPlusOneViewGenerator, ADLGenerator
from visualizer import ModelVisualizer
from pathlib import Path
import hashlib
import base64
from architectural_model.utils.service_health import service_health
from architectural_model.middleware.service_check import ServiceCheckMiddleware

app = FastAPI(
    title="Architectural Model Converter",
    description="A microservice that converts code into architectural models",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.add_middleware(ServiceCheckMiddleware)

class CodeAnalysisRequest(BaseModel):
    code: str
    target_architecture: str

class CodeAnalysisResponse(BaseModel):
    model: str
    components: list
    relationships: list
    metadata: dict
    representation: Union[str, Dict[str, Any]] = None
    visualization: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Architectural Model Converter API"}

@app.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze the provided code and convert it to the specified architectural model
    """
    # Initialize code analyzer
    analyzer = CodeAnalyzer(request.code)
    analysis_result = analyzer.analyze()

    # Generate the requested architectural model
    representation = None
    visualization = None
    target_arch = request.target_architecture.lower()
    
    try:
        if target_arch == "uml":
            generator = UMLGenerator(analysis_result)
            representation = generator.generate_class_diagram()
            visualization = ModelVisualizer.visualize_uml(representation)
        elif target_arch == "4+1":
            generator = FourPlusOneViewGenerator(analysis_result)
            representation = generator.generate_views()
            visualization = ModelVisualizer.visualize_4plus1(representation)
        elif target_arch == "adl":
            generator = ADLGenerator(analysis_result)
            representation = generator.generate_adl()
            visualization = ModelVisualizer.visualize_adl(representation)
        else:
            raise ValueError(f"Unsupported architecture type: {request.target_architecture}")

        return CodeAnalysisResponse(
            model=request.target_architecture,
            components=analysis_result["components"],
            relationships=analysis_result["relationships"],
            metadata={
                "language": "python",
                "total_components": len(analysis_result["components"]),
                "total_relationships": len(analysis_result["relationships"])
            },
            representation=representation,
            visualization=visualization
        )
    except Exception as e:
        raise ValueError(f"Error generating {target_arch} model: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a code file for analysis
    """
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}

@app.post("/visualize/upload", response_class=HTMLResponse)
async def visualize_uploaded_file(file: UploadFile = File(...), model_type: str = "uml"):
    """
    Upload a code file and visualize it
    """
    content = await file.read()
    code = content.decode("utf-8")
    
    # Create a unique identifier for this visualization
    code_hash = base64.urlsafe_b64encode(hashlib.md5(code.encode()).digest()).decode()[:8]
    
    # Store the code temporarily (in a real app, you'd use a database)
    temp_dir = Path("temp_visualizations")
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / f"{code_hash}_{model_type}.py"
    temp_file.write_text(code)
    
    # Return a page with a link to the visualization
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visualization Ready</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 20px;
            }}
            .button:hover {{
                background-color: #45a049;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Visualization Ready!</h1>
            <p>Your code has been successfully uploaded and processed.</p>
            <a href="/visualize/{model_type}?code_hash={code_hash}" class="button">View Visualization</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/visualize/{model_type}", response_class=HTMLResponse)
async def visualize_model(model_type: str, code_hash: str = None):
    """
    Direct visualization endpoint
    """
    if not code_hash:
        return HTMLResponse(content="No code hash provided", status_code=400)
    
    # Read the code from the temporary file
    temp_file = Path("temp_visualizations") / f"{code_hash}_{model_type}.py"
    if not temp_file.exists():
        return HTMLResponse(content="Visualization not found or expired", status_code=404)
    
    code = temp_file.read_text()
    
    analyzer = CodeAnalyzer(code)
    analysis_result = analyzer.analyze()
    
    if model_type.lower() == "uml":
        generator = UMLGenerator(analysis_result)
        uml_dot = generator.generate_class_diagram()
        visualization = ModelVisualizer.visualize_uml(uml_dot)
    elif model_type.lower() == "4+1":
        generator = FourPlusOneViewGenerator(analysis_result)
        views = generator.generate_views()
        visualization = ModelVisualizer.visualize_4plus1(views)
    elif model_type.lower() == "adl":
        generator = ADLGenerator(analysis_result)
        adl_text = generator.generate_adl()
        visualization = ModelVisualizer.visualize_adl(adl_text)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    # Create a complete HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{model_type.upper()} Visualization</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ text-align: center; color: #333; }}
            .visualization {{ width: 100%; height: 800px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{model_type.upper()} Visualization</h1>
            <div class="visualization">
                {visualization}
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint for the service."""
    return {"status": "healthy"}

@app.get("/services/status")
async def check_services():
    """Check the status of all dependent services."""
    status = await service_health.check_all_services()
    return status

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 