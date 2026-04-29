# Deployment

This section provides cookbooks for deploying Foundation-Sec models on different platforms. Choose the one that fits your infrastructure, budget, and workflow.

## Platform Comparison

| | [SageMaker](./sagemaker/) | [Bedrock](./bedrock/) | [Baseten](./baseten/) |
|---|---|---|---|
| **Provider** | AWS | AWS | Baseten |
| **Infrastructure** | You choose instance type + container | Fully managed | Fully managed |
| **Billing** | Per-hour while endpoint is running | Always-on while model is imported | Per-inference (scale to zero when idle) |
| **API access** | AWS SDK (`invoke_endpoint`) | AWS SDK (`invoke_model`) | HTTP API (OpenAI-compatible) |
| **Quantization** | Yes (GGUF supported) | No (BF16 only) | Yes |
| **Reasoning trace parsing** | Native (vLLM `minimax_m2` parser) | Manual (parse `<think>` tags from output) | Native (vLLM) |
| **Team sharing** | Share endpoint name (AWS SDK access needed) | Share Model ARN (AWS SDK access needed) | Share API key + endpoint URL |
| **Setup effort** | Low (SageMaker SDK) | Low (import from S3) | Low (Truss CLI) |
| **Shutdown** | Delete endpoint | Delete imported model | Scale to zero |
| **Regions** | All SageMaker regions | `us-east-1`, `us-east-2`, `us-west-2`, `eu-central-1` | N/A |

## Which platform should I use?

**Choose [SageMaker](./sagemaker/) if:**
- You're on AWS and want per-hour billing (good for development and bursty workloads)
- You need quantized models (GGUF) for faster inference or lower cost
- You want control over instance type, container image, and serving configuration

**Choose [Bedrock](./bedrock/) if:**
- You want zero infrastructure management. No containers, instances, or serving config
- You're already using Bedrock for other models and want everything in one place
- You need always-on availability without managing endpoint lifecycle

**Choose [Baseten](./baseten/) if:**
- You want per-inference billing (pay only when the model is called)
- You need auto-scaling to zero when idle
- You prefer a platform-agnostic setup outside of AWS
