FROM python:3.9-slim

WORKDIR /app

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package files
COPY setup.py .
COPY version_control/ ./version_control/

# Install the package in development mode
RUN pip install -e .

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Create static directory
RUN mkdir -p /app/static

# Copy static files
COPY static/ /app/static/

# Create directory for repositories
RUN mkdir -p /app/repositories

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "version_control.main:app", "--host", "0.0.0.0", "--port", "8000"]
