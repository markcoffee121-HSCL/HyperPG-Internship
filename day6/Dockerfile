FROM python:3.10-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Docker Image Labels for Hypercycle Node Manager
LABEL GPUS="0"
LABEL CPU_SHARES="512"
LABEL description="File Processor AIM - Accepts text files and returns line/word count analysis"

# Health check labels
LABEL HEALTH_URI="/health"
LABEL HEALTH_RETRIES="3"
LABEL HEALTH_TIMEOUT="400"
LABEL HEALTH_INTERVAL="5000"

WORKDIR /opt

# Install system dependencies (git required for pyhypercycle_aim)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port 4000 (Hypercycle standard)
EXPOSE 4000

# Set PORT environment variable
ENV PORT=4000

# Run the application
CMD ["python", "main.py"]