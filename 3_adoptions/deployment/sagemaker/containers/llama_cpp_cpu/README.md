# llama.cpp CPU container (SageMaker)

This builds a SageMaker compatible image. It is a minimal adapter over the official `ghcr.io/ggml-org/llama.cpp:server` exposing:
- /ping
- /invocations (expects OpenAI-style `messages`)

## Build and push
- Build (tags local and ECR):

  ```make build REPO_NAME=fdtn-llama-cpp-cpu REGION=us-west-2 VERSION=v1```
- Push to ECR:

  ```make publish REPO_NAME=fdtn-llama-cpp-cpu REGION=us-west-2 VERSION=v1```

This would push the following images to your AWS ECR:
```
<ACCOUNT_ID>.dkr.ecr.us-west-2.amazonaws.com/fdtn-llama-cpp-cpu:latest
<ACCOUNT_ID>.dkr.ecr.us-west-2.amazonaws.com/fdtn-llama-cpp-cpu:v1
```
These images can then be used to run a GGUF quantized model on SageMaker using the cookbooks in the [foundation_sec_8b_instruct_quantized](../foundation_sec_8b_instruct_quantized/cpu) directory.

## Notes:
- Set `HF_MODEL_ID` to the GGUF model repo (default is `fdtn-ai/Foundation-Sec-8B-Instruct-Q8_0-GGUF`).
- Container listens on port `8080` for SageMaker.
