# Use the official Python base image
FROM python:3.9-slim

# Set working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code into the container
COPY ./ /app/

# Set the PYTHONPATH environment variable to the app directory
ENV PYTHONPATH=/app

# Expose the port the app will run on
EXPOSE 9006

# Run FastAPI with Uvicorn as a module (ensure it uses the correct path)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9006"]
