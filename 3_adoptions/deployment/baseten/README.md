# Deployment and Inference with Baseten

[Baseten](https://www.baseten.co/) provides flexible and scalable infrastructure for deploying and managing machine learning models. These sample code bundles provide guides for deploying FoundationSec models to Baseten for inference. A deployment in Baseten is a containerized instance of a model that is automatically wrapped in a REST API endpoint. Baseten supports a predict and async-predict API endpoint as well as Open AI compatible servers. <br>
Please see the [Baseten Docs](https://docs.baseten.co/overview) for more details on setting up scalable deployments with Baseten. <br>
Please note that we assume you already have Baseten accounts or contracts and are aware that deployments will incur costs.

## Deploy the model
1. Install Truss:
```bash
pip install --upgrade truss
```
2. Copy the foundation_sec_8b folder to the current directory. If you want to deploy a FoundationSec model with a vLLM server to Baseten, copy "foundation_sec_8b_vLLM" folder instead. Note that you can change the FoundationSec model or version in the "repo_id" of the "model_metadata" section if you'd like.

3. Deploy the model:
```bash
truss push # You would be prompted to provide API key. If you don't have one, you can get it from the console.
```
4. Run Inference
Once it's deployed, you can run inference using the endpoint.

**Example 1: Baseten [Predict API Endpoint](https://docs.baseten.co/inference/calling-your-model#predict-api-endpoints)**

```python
import requests

ENDPOINT_URL = "" # Replace with your endpoint URL
API_KEY = "" # Replace with your API key

def inference(prompt):
    data = {'prompt': prompt}
    # If you want to add your own generation_args, you can do so like this:
    # data['generate_args'] = YOUR_GENERATION_ARGS
    response = requests.post(
        ENDPOINT_URL,
        headers={"Authorization": f"Api-Key {API_KEY}"},
        json=data,
    )
    return response.text
```

`YOUR_GENERATION_ARGS` is a dictionary containing generation arguments. <br>

For more details, refer to the [configuration section of quickstart guide](https://github.com/RobustIntelligence/foundation-ai-cookbook/blob/main/1_quickstarts/Quickstart_Foundation-Sec-8B.ipynb).

**Example 2: Baseten deployment with the [OpenAI SDK](https://docs.baseten.co/inference/calling-your-model#openai-sdk)**

Baseten's Engine Builder supports setting up OpenAI compatible servers. This is useful to run inference with a vLLM server using the [OpenAI API](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html), our recommended method for utulizing constrained decoding backend.

OpenAI's Chat Completions API:

```python

import requests

ENDPOINT_URL = "" # Replace with your endpoint URL
API_KEY = "" # Replace with your API key


def create_request(prompt: str, schema: dict) -> dict:
    return {
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "response_schema",
                "schema": schema,
            },
        }
    }

def inference(prompt: str, schema: dict, url=ENDPOINT_URL) -> str:
    headers = {
        "Authorization": f"Api-Key {API_KEY}"
    }
    response = requests.post(
        url,
        headers=headers,
        json=create_request(prompt, schema),
    )
    return response.json()

```

For example schemas using the constrained decoding baceknd, see "Structured_Outputs.ipynb" under 3_adoptions/deployment/integrations. 