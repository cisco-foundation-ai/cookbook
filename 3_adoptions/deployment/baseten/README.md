# Deployment and Inference with Baseten

[Baseten](https://www.baseten.co/) can be used to deploy the base model for inference. <br>
Sample code bundles are provided for deployment on the platform. <br>
Please note that we assume you already have Baseten accounts or contracts and are aware that deployments will incur costs.

## Deploy the model
1. Install Truss:
```bash
pip install --upgrade truss
```
2. Copy the foundation_sec_8b folder to the current directory. If you want to deploy a FoundationSec model with a vLLM server to Baseten, copy "foundation_sec_8b_vLLM" instead. Note that you can change the FoundationSec model or version in the "repo_id" of the "model_metadata" section if you'd like.
3. Deploy the model:
```bash
truss push # You would be prompted to provide API key. If you don't have one, you can get it from the console.
```
4. Run Inference
Once it's deployed, you can run inference using the endpoint.
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

Example for calling inference with vLLM server & constrained decoding backend. Note that vLLM uses the OpenAI API:

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

`YOUR_GENERATION_ARGS` is a dictionary containing generation arguments. <br>
For more details, refer to the [configuration section of quickstart guide](https://github.com/RobustIntelligence/foundation-ai-cookbook/blob/main/1_quickstarts/Quickstart_Foundation-Sec-8B.ipynb).
