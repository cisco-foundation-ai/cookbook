#!/usr/bin/env bash
set -euo pipefail

HF_MODEL_ID="${HF_MODEL_ID:-fdtn-ai/Foundation-Sec-8B-Instruct-Q8_0-GGUF}"
CTX="${CTX:-8192}"
THREADS="${THREADS:-$(nproc)}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
SAGEMAKER_PORT="${SAGEMAKER_PORT:-8080}"
HOST="${HOST:-0.0.0.0}"
EXTRA_LLAMA_ARGS="${EXTRA_LLAMA_ARGS:-}"   # e.g. "--mlock --parallel 2"

# Start llama-server
echo "[launch] starting llama-server: model=${HF_MODEL_ID} ctx=${CTX} threads=${THREADS} port=${LLAMA_PORT}"
cd /app && ./llama-server \
  -hf "${HF_MODEL_ID}" \
  -c "${CTX}" \
  -t "${THREADS}" \
  --host "${HOST}" \
  --port "${LLAMA_PORT}" \
  ${EXTRA_LLAMA_ARGS} &

LLAMA_PID=$!

# Wait for llama-server to be ready
echo "[wait] waiting for llama-server /health on :${LLAMA_PORT}"
for i in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/health" >/dev/null 2>&1; then
    echo "[ready] llama-server is healthy"
    break
  fi
  sleep 1
done

# Start the SageMaker shim on 8080
echo "[launch] starting shim on :${SAGEMAKER_PORT}"
uvicorn app:app --host 0.0.0.0 --port "${SAGEMAKER_PORT}" &
SHIM_PID=$!

# Forward termination signals to both processes
trap "echo '[stop] shutting down'; kill -TERM ${SHIM_PID} || true; kill -TERM ${LLAMA_PID} || true; wait" SIGINT SIGTERM

wait -n
