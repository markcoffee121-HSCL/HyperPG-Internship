FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY orchestrator.py .

# Copy frontend files
COPY templates/ templates/
COPY static/ static/

# Expose port
EXPOSE 4000

# Metadata
LABEL description="HyperPG Pipeline Orchestrator - Complete research report generation"
LABEL author="Raijin - HyperPG Capstone"

CMD ["python", "app.py"]