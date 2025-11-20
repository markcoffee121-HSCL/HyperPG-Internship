FROM python:3.10-slim

LABEL GPUS="0"
LABEL CPU_SHARES="512"
LABEL HEALTH_URI="/health"
LABEL HEALTH_RETRIES="3"
LABEL HEALTH_TIMEOUT="400"
LABEL HEALTH_INTERVAL="5000"
LABEL description="Day 8 LLM Summarizer AIM - Uses Groq for text summarization"
LABEL author="Raijin - HyperPG Intern"

WORKDIR /app

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 4000

CMD ["python", "main.py"]
