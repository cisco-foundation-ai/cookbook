# Foundation-Sec-8B-Instruct-Q8_0-GGUF Model - SageMaker Deployment

This directory contains cookbooks for deploying and running inference with the **Foundation-Sec-8B-Instruct-Q8_0-GGUF model** on Amazon SageMaker.

We provide two sample notebooks:
1. Deploy Models: Deploy Foundation AI models on SageMaker and create an inference endpoint ([link](./deploy.ipynb)).
2. Run Inference: Perform inference using the created endpoint ([link](./inference.ipynb)).

## Prerequisites

This notebook uses the [llama-cpp](https://github.com/ggerganov/llama.cpp) library to run inference on the CPU. You can use the guide in [llama_cpp_cpu](../containers/llama_cpp_cpu/README.md) to build and push a custom docker image to your ECR. This builds an image that is a minimal adapter over the official `ghcr.io/ggml-org/llama.cpp:server` and is compatible with SageMaker.

Please note that we assume you already have AWS accounts or contracts and are aware that deployments will incur costs.

For questions about this model or deployment issues, please refer to the main [SageMaker README](../README.md) or consult the AWS SageMaker documentation.
