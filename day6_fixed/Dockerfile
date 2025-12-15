FROM python:3.10-slim

WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

EXPOSE 4000

LABEL description="File Processor AIM - Fixed with PDF/DOCX support"

CMD ["python", "main.py"]