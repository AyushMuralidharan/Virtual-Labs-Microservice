FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package files
COPY setup.py .
COPY architectural_model/ ./architectural_model/

# Install the package in development mode
RUN pip install -e .

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Create static directory
RUN mkdir -p /app/static

# Copy static files
COPY static/ /app/static/

# Create directory for temporary visualizations
RUN mkdir -p temp_visualizations

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "architectural_model.main:app", "--host", "0.0.0.0", "--port", "8000"] 