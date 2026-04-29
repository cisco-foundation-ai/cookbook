#!/usr/bin/env bash
set -euo pipefail

echo "[startup] Launching vLLM..."
vllm serve fdtn-ai/Foundation-Sec-8B-Reasoning \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --max-model-len 65536 \
  --reasoning-parser minimax_m2 \
  --trust-remote-code
