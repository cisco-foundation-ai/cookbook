# Foundation-Sec-8B-Reasoning Model - SageMaker Deployment

This directory contains cookbooks for deploying and running inference with the **Foundation-Sec-8B-Reasoning** model on Amazon SageMaker.

This is a reasoning model that produces chain-of-thought tokens, so it requires:
- A vLLM container image with the `minimax_m2` reasoning parser
- A `g6e` family instance (or better) to handle the higher token throughput from reasoning traces

We provide two sample notebooks:
1. Deploy Model: Deploy the Foundation-Sec-8B-Reasoning model on SageMaker and create an inference endpoint ([link](./deploy.ipynb)).
2. Run Inference: Perform inference using the created endpoint ([link](./inference.ipynb)).

Please note that we assume you already have AWS accounts or contracts and are aware that deployments will incur costs.

## Important Notes

- **Env var prefix:** This vLLM container requires `SM_VLLM_*` prefixed env vars. Do not use DJL-style vars (`HF_MODEL_ID`, `OPTION_REASONING_PARSER`, etc.) — they will be silently ignored.
- **Instance type:** Use `g6e` family (e.g., `ml.g6e.2xlarge`) or better. Lower-tier instances like `g6.xlarge` are not recommended for this reasoning model.

## Troubleshooting

If you see raw `<think>`/`</think>` tokens in the response instead of a separate `reasoning_content` field, the reasoning parser is not configured. Check CloudWatch logs for the `non-default args` line. It should include `'reasoning_parser': 'minimax_m2'`. If it only shows `{'port': 8080}`, the env vars are not being read.

For additional questions, please refer to the main [SageMaker README](../README.md) or consult the AWS SageMaker documentation.
