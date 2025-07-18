FROM python:3.9-bullseye

WORKDIR /app

# Install PostgreSQL client and build dependencies
RUN apt-get update && \
    apt-get install -y postgresql-client build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]