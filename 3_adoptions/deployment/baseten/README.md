# Deployment and Inference with Baseten

[Baseten](https://www.baseten.co/) provides flexible and scalable infrastructure for deploying and managing machine learning models. These sample code bundles provide guides for deploying FoundationSec models to Baseten for inference. A deployment in Baseten is a containerized instance of a model that is automatically wrapped in a REST API endpoint. Baseten supports a predict and async-predict API endpoint as well as Open AI compatible servers. <br>
Please see the [Baseten Docs](https://docs.baseten.co/overview) for more details on setting up scalable deployments with Baseten. <br>
Please note that we assume you already have Baseten accounts or contracts and are aware that deployments will incur costs.

## Deploy the model
1. Install Truss:
```bash
pip install --upgrade truss
```
2. Copy the deploy script folder to the current directory. 
* To deploy a Foundation-Sec-8B model, copy the `foundation_sec_8b` folder. 
* Alternatively, to deploy the Foundation-Sec-8B model **with a vLLM server** to Baseten, copy `foundation_sec_8b_vLLM` folder instead. Note that you can change the FoundationSec model or version in the "repo_id" of the "model_metadata" section if you'd like.
* To deploy a **Foundation-Sec-8B-Reasoning** model to Baseten, copy the `foundation-sec-8b-reasoning` folder. This script deploys the **Reasoning Model** with a vLLM server.

3. Deploy the model:
```bash
truss push # You would be prompted to provide API key. If you don't have one, you can get it from the console.
```
4. Run Inference

Once it's deployed, you can run inference using the endpoint. Do note that the endpoint URLs are different depending on the request type.

**Example 1: Baseten [Chat Completion API Endpoint](https://docs.baseten.co/reference/inference-api/overview)** 

```python
import requests

ENDPOINT_URL = "" # Replace with your endpoint URL. Example: https://model-{model_id}.api.baseten.co/environments/production/sync/v1/chat/completions
API_KEY = "" # Replace with your API key

def inference(prompt):
    data = {'messages': [{"role": "user", "content": prompt}]}
    # If you want to add your own generation_args, you can do so like this: data['generate_args'] = YOUR_GENERATION_ARGS
    # For example: data['max_tokens'] = 2000
    response = requests.post(
        ENDPOINT_URL,
        headers={"Authorization": f"Api-Key {API_KEY}"},
        json=data,
    )
    return response.text
```

**Example 2: Baseten [Predict API Endpoint](https://docs.baseten.co/inference/calling-your-model#predict-api-endpoints)**

```python
import requests

ENDPOINT_URL = "" # Replace with your endpoint URL. Example: https://model-{model_id}.api.baseten.co/environments/production/predict
API_KEY = "" # Replace with your API key

def inference(prompt):
    data = {'prompt': prompt}
    # If you want to add your own generation_args, you can do so like this: data['generate_args'] = YOUR_GENERATION_ARGS
    # For example: data['max_tokens'] = 2000
    response = requests.post(
        ENDPOINT_URL,
        headers={"Authorization": f"Api-Key {API_KEY}"},
        json=data,
    )
    return response.text
```

**Example 3: Baseten deployment with the [OpenAI SDK](https://docs.baseten.co/inference/calling-your-model#openai-sdk)**


```python

import requests
from openai import OpenAI

ENDPOINT_URL = "" # Replace with your endpoint URL. Exzample: https://model-{model_id}.api.baseten.co/environments/production/sync/v1
API_KEY = "" # Replace with your API key

client = OpenAI(
    base_url=ENDPOINT_URL,
    api_key=API_KEY,
)

def inference(prompt):
    response = client.chat.completions.create(
        model="",  # must match --served-model-name in the deployment. For example: fdtn-ai/Foundation-Sec-8B-Reasoning
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response

```
