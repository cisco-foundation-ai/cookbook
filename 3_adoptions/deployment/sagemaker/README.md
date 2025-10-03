# Deployment and Inference with Amazon SageMaker AI

This directory contains cookbooks for deploying and running inference with Foundation AI models on Amazon SageMaker. We provide examples for both our base model and instruct-tuned model.

## Available Models

### Foundation-Sec-8B (Base Model)
Our foundational 8B parameter model trained for security-focused tasks.
- **Deploy**: [foundation_sec_8b/deploy.ipynb](./foundation_sec_8b/deploy.ipynb)
- **Inference**: [foundation_sec_8b/inference.ipynb](./foundation_sec_8b/inference.ipynb)
- **Documentation**: [foundation_sec_8b/README.md](./foundation_sec_8b/README.md)

### Foundation-Sec-8B-Instruct (IFT Model)
Our instruction-fine-tuned model optimized for chat and instruction-following tasks.
- **Deploy**: [foundation_sec_8b_instruct/deploy.ipynb](./foundation_sec_8b_instruct/deploy.ipynb)
- **Inference**: [foundation_sec_8b_instruct/inference.ipynb](./foundation_sec_8b_instruct/inference.ipynb)
- **Documentation**: [foundation_sec_8b_instruct/README.md](./foundation_sec_8b_instruct/README.md)

### Foundation-Sec-8B-Instruct-Q8_0-GGUF (8 bit quantized IFT Model)

- **Deploy**: [foundation_sec_8b_instruct_quantized/deploy.ipynb](./foundation_sec_8b_instruct_quantized/cpu/deploy.ipynb)
- **Inference**: [foundation_sec_8b_instruct_quantized/inference.ipynb](./foundation_sec_8b_instruct_quantized/cpu/inference.ipynb)
- **Documentation**: [foundation_sec_8b_instruct_quantized/README.md](./foundation_sec_8b_instruct_quantized/cpu/README.md)

## Getting Started

1. Choose the model that best fits your use case:
   - **Base Model**: Better for completion tasks, fine-tuning, or when you need maximum flexibility
   - **Instruct Model**: Better for chat applications, Q&A, and instruction-following tasks

2. Navigate to the appropriate model directory
3. Start with the `deploy.ipynb` notebook to set up your SageMaker endpoint
4. Use the `inference.ipynb` notebook to test your deployed model

## Prerequisites

- AWS account with SageMaker access
- Appropriate IAM permissions for SageMaker operations
- JupyterLab environment on SageMaker (recommended)

For more details on setting up JupyterLab on SageMaker, visit: https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-jl.html

## Note

Please note that we assume you already have AWS accounts or contracts and are aware that deployments will incur costs.
