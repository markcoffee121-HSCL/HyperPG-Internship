FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY query_decomposer.py .
COPY source_evaluator.py .
COPY research_engine.py .
COPY main.py .

EXPOSE 4000

LABEL HEALTH_URI="/health"
LABEL HEALTH_RETRIES="3"
LABEL HEALTH_TIMEOUT="400"
LABEL HEALTH_INTERVAL="5000"

LABEL CPU_SHARES="512"
LABEL GPUS="0"

LABEL description="Research Agent AIM - Intelligent web research with source evaluation"
LABEL author="Raijin - HyperPG Capstone"

CMD ["python", "main.py"]