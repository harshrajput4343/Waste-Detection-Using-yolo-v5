# Use Python 3.10 as base image (matching your environment)
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Update package lists and install system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    awscli \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    unzip \
    git \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p data artifacts yolov5/runs

# Expose Flask port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8080

# Run the application
CMD ["python", "app.py"]
