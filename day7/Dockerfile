FROM python:3.10-slim

LABEL GPUS="0"
LABEL CPU_SHARES="512"
LABEL HEALTH_URI="/health"
LABEL HEALTH_RETRIES="3"
LABEL HEALTH_TIMEOUT="400"
LABEL HEALTH_INTERVAL="5000"
LABEL description="Day 7 Summarizer AIM - Calls File Processor AIM for analysis"
LABEL author="Raijin - HyperPG Intern"

WORKDIR /app

# Install git (needed for pyhypercycle_aim)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 4000

CMD ["python", "main.py"]
