# Foundation-Sec-8B-Reasoning Model - Bedrock Deployment

This directory contains cookbooks for deploying and running inference with the **Foundation-Sec-8B-Reasoning** model on Amazon Bedrock via Custom Model Import.

We provide two sample notebooks:
1. Deploy Model: Import the model into Bedrock from S3 ([link](./deploy.ipynb)).
2. Run Inference: Perform inference using the imported model ([link](./inference.ipynb)).

Please note that we assume you already have AWS accounts or contracts and are aware that deployments will incur costs.

## Important Notes

- **API format:** Bedrock's `invoke_model` accepts OpenAI-style messages for imported models — no tokenizer or manual chat template needed.
- **Reasoning parsing:** The model outputs `<think>...</think>` reasoning traces inline. The inference notebook includes a parser to split the reasoning from the final answer.
- **Always-on billing:** Imported models bill continuously (~$1,080-1,440/month for 8B). Delete the imported model when not in use.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModelNotReadyException` | Cold start after import | Wait ~5 minutes and retry |
| `AccessDeniedException` | Missing Bedrock or PassRole permissions | Check IAM policies |
| Raw `<think>` tags in output | Model not triggering reasoning | Verify the model was imported after November 2025 |

For additional questions, please refer to the main [Bedrock README](../README.md) or consult the [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html).
