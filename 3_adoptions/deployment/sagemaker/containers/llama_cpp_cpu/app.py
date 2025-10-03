import os
import requests
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI()
LLAMA_URL = f"http://127.0.0.1:{os.getenv('LLAMA_PORT', '8081')}"
MODEL_NAME = os.getenv("MODEL_NAME", "local")  # forwarded to OpenAI-like API


@app.get("/ping")
def ping():
    """
    SageMaker health check to llama-server /health
    """
    r = requests.get(f"{LLAMA_URL}/health", timeout=5)
    return PlainTextResponse(
        "OK" if r.ok else "FAIL", status_code=(200 if r.ok else 503)
    )


@app.post("/invocations")
async def invocations(req: Request):
    """
    Accepts {"messages": [...], ...} and forwards to /v1/chat/completions
    Returns llama-server's JSON as-is.
    """
    data = await req.json()
    timeout = int(os.getenv("TIMEOUT_SECS", "600"))

    if (
        "messages" not in data
        or not isinstance(data["messages"], list)
        or len(data["messages"]) == 0
    ):
        return JSONResponse(
            {"error": "Missing 'messages' (list) in JSON body"}, status_code=400
        )

    payload = {"model": data.get("model", MODEL_NAME), **data}
    url = f"{LLAMA_URL}/v1/chat/completions"
    r = requests.post(url, json=payload, timeout=timeout)

    try:
        return JSONResponse(r.json(), status_code=r.status_code)
    except ValueError:
        return Response(
            content=r.text,
            status_code=r.status_code,
            media_type=r.headers.get("content-type", "text/plain"),
        )
