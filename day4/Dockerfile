FROM python:3.10-slim

# Set environment to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Docker Image Labels for Hypercycle Node Manager
LABEL GPUS="0"
LABEL description="Day 4 Custom AIM - Hello Node Example"
LABEL author="Raijin - HyperPG Intern"

# Set working directory
WORKDIR /app

# Install system dependencies including git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt .
COPY main.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 4000 (default AIM port)
EXPOSE 4000

# Run the application
CMD ["python3", "main.py"]
