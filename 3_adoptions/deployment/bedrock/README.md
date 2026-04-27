# Deployment and Inference with Amazon Bedrock

This directory contains cookbooks for deploying and running inference with Foundation AI models on Amazon Bedrock using Custom Model Import. Model artifacts are imported from S3 and Bedrock creates a fully managed endpoint. No containers or instance types to configure.

## Available Models

### Foundation-Sec-8B-Reasoning (Reasoning Model)
Our reasoning model that produces chain-of-thought traces for security tasks.
- **Deploy**: [foundation_sec_8b_reasoning/deploy.ipynb](./foundation_sec_8b_reasoning/deploy.ipynb)
- **Inference**: [foundation_sec_8b_reasoning/inference.ipynb](./foundation_sec_8b_reasoning/inference.ipynb)
- **Documentation**: [foundation_sec_8b_reasoning/README.md](./foundation_sec_8b_reasoning/README.md)

## Getting Started

1. Upload your model to S3 using the included [`upload_hf_to_s3.py`](./upload_hf_to_s3.py) helper script (or bring your own S3 artifacts)
2. Import the model into Bedrock using `deploy.ipynb`, or through the [AWS Console](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html)
3. Use the `inference.ipynb` notebook to test your imported model

## Prerequisites

- AWS account with Bedrock access in a supported region (`us-east-1`, `us-east-2`, `us-west-2`, or `eu-central-1`)
- Model artifacts uploaded to S3
- IAM user with S3, Bedrock, and PassRole permissions
- A Bedrock service role with S3 read access

## Note

Bedrock imported models bill **continuously** (~$1,080-1,440/month for 8B). Delete them when not in use.
