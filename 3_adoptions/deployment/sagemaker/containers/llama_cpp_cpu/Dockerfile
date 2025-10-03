# Base: official llama.cpp server image
FROM ghcr.io/ggml-org/llama.cpp:server

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Python packages: FastAPI + Uvicorn + Requests
RUN pip3 install --no-cache-dir fastapi uvicorn[standard] requests

# SageMaker expects these directories
RUN mkdir -p /opt/ml/model /opt/ml/input /opt/ml/output /opt/program
WORKDIR /opt/program

COPY app.py serve.sh ./
RUN chmod +x /opt/program/serve.sh

# Defaults for llama cpp; override via SageMaker env vars if needed
ENV HF_MODEL_ID=fdtn-ai/Foundation-Sec-8B-Instruct-Q8_0-GGUF
ENV CTX=8192
ENV THREADS=16
ENV LLAMA_PORT=8081
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose port 8080 for SageMaker
EXPOSE 8080

ENTRYPOINT ["/opt/program/serve.sh"]
