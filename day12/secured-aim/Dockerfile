FROM python:3.8.17-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /opt

# Install system dependencies including git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip python3-dev build-essential git && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy application code
COPY app app

# Expose port
EXPOSE 4000

# Run the application
CMD python3 ./app/main.py