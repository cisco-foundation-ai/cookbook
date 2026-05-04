import json
import re
import requests

MAX_TOKENS = 8192
TEMPERATURE = 0.3


class ReasoningModelClient:

    def __init__(self, max_tokens: int = MAX_TOKENS, temperature: float = TEMPERATURE):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._deployment_type: str = None

    @classmethod
    def from_transformers(
        cls,
        model_id: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ) -> "ReasoningModelClient":
        """
        Create a client using a local HuggingFace Transformers model.

        Args:
            model_id (str): HuggingFace model ID.
                            Example: "fdtn-ai/Foundation-Sec-8B-Reasoning"
            max_tokens (int): Maximum tokens to generate.
            temperature (float): Sampling temperature.

        Returns:
            ReasoningModelClient: Configured client instance.
        """
        if not model_id or not model_id.strip():
            raise ValueError("[transformers] 'model_id' must be a non-empty string.")

        instance = cls(max_tokens=max_tokens, temperature=temperature)
        instance._deployment_type = "transformers"
        instance._init_transformers(model_id)
        return instance

    @classmethod
    def from_sagemaker(
        cls,
        endpoint_name: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ) -> "ReasoningModelClient":
        """
        Create a client using an AWS SageMaker endpoint.

        Args:
            endpoint_name (str): The name of the SageMaker inference endpoint.
            max_tokens (int): Maximum tokens to generate.
            temperature (float): Sampling temperature.

        Returns:
            ReasoningModelClient: Configured client instance.
        """
        if not endpoint_name or not endpoint_name.strip():
            raise ValueError("[sagemaker] 'endpoint_name' must be a non-empty string.")

        instance = cls(max_tokens=max_tokens, temperature=temperature)
        instance._deployment_type = "sagemaker"
        instance._init_sagemaker(endpoint_name)
        return instance

    @classmethod
    def from_baseten(
        cls,
        endpoint_url: str,
        api_key: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ) -> "ReasoningModelClient":
        """
        Create a client using a Baseten deployment endpoint.

        Args:
            endpoint_url (str): Full Baseten endpoint URL.
                                Example: "https://XXXXX.api.baseten.co/environments/production/sync/v1/chat/completions"
            api_key (str): Baseten API key.
            max_tokens (int): Maximum tokens to generate.
            temperature (float): Sampling temperature.

        Returns:
            ReasoningModelClient: Configured client instance.
        """
        missing = [name for name, val in [("endpoint_url", endpoint_url), ("api_key", api_key)] if not val or not val.strip()]
        if missing:
            raise ValueError(f"[baseten] The following arguments are missing or empty: {missing}")

        instance = cls(max_tokens=max_tokens, temperature=temperature)
        instance._deployment_type = "baseten"
        instance._init_baseten(endpoint_url, api_key)
        return instance

    @classmethod
    def from_bedrock(
        cls,
        region: str,
        model_arn: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ) -> "ReasoningModelClient":
        """
        Create a client using an AWS Bedrock imported model.

        Args:
            region (str): AWS region name. Example: "us-east-1"
            model_arn (str): ARN of the imported Bedrock model.
            max_tokens (int): Maximum tokens to generate.
            temperature (float): Sampling temperature.

        Returns:
            ReasoningModelClient: Configured client instance.
        """
        missing = [name for name, val in [("region", region), ("model_arn", model_arn)] if not val or not val.strip()]
        if missing:
            raise ValueError(f"[bedrock] The following arguments are missing or empty: {missing}")

        instance = cls(max_tokens=max_tokens, temperature=temperature)
        instance._deployment_type = "bedrock"
        instance._init_bedrock(region, model_arn)
        return instance

    def _init_transformers(self, model_id: str):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        def _get_device() -> str:
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            return "cpu"

        self._device = _get_device()
        self._tokenizer = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=model_id,
            device_map="auto",
            torch_dtype=torch.float32,
        )
        self._generation_args = {
            "max_new_tokens": self.max_tokens,
            "temperature":    self.temperature,
            "do_sample":      True,
            "use_cache":      True,
            "eos_token_id":   self._tokenizer.eos_token_id,
            "pad_token_id":   self._tokenizer.pad_token_id,
        }

    def _init_sagemaker(self, endpoint_name: str):
        import boto3
        self._endpoint_name = endpoint_name
        self._sagemaker_runtime = boto3.client("sagemaker-runtime")

    def _init_baseten(self, endpoint_url: str, api_key: str):
        self._endpoint_url = endpoint_url
        self._api_key = api_key

    def _init_bedrock(self, region: str, model_arn: str):
        import boto3
        self._model_arn = model_arn
        self._bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)

    @staticmethod
    def _extract_reasoning_from_message(message: dict) -> tuple[str, str]:
        """Extract reasoning and answer from a vLLM-style message dict."""
        reasoning = message.get("reasoning_content") or message.get("reasoning", "")
        answer = message.get("content", "")
        return reasoning, answer

    @staticmethod
    def _parse_bedrock_reasoning(raw_output: str) -> tuple[str, str]:
        """Split Bedrock model output into a reasoning trace and final answer."""
        match = re.search(r"</think>", raw_output, re.IGNORECASE)
        if match:
            reasoning = raw_output[:match.start()]
            content = raw_output[match.end():]
            reasoning = re.sub(r"^\s*<think>\\s*", "", reasoning, flags=re.IGNORECASE)
            return reasoning.strip(), content.strip()
        return "", raw_output.strip()

    def chat_generation(self, user_prompt: str) -> tuple[str, str]:
        """
        Run inference against the configured deployment backend.

        Args:
            user_prompt (str): The user message to send to the model.

        Returns:
            tuple[str, str]: (reasoning, answer)
                - reasoning (str): The model's internal chain-of-thought (may be empty).
                - answer (str): The final response from the model.
        """
        handlers = {
            "transformers": self._generate_transformers,
            "sagemaker":    self._generate_sagemaker,
            "baseten":      self._generate_baseten,
            "bedrock":      self._generate_bedrock,
        }
        return handlers[self._deployment_type](user_prompt)

    def _generate_transformers(self, user_prompt: str) -> tuple[str, str]:
        import torch

        messages = [{"role": "user", "content": user_prompt}]
        inputs = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        think_token = "<think>\n"
        if not inputs.endswith(think_token):
            inputs += think_token

        inputs = self._tokenizer(inputs, return_tensors="pt").to(self._device)

        with torch.no_grad():
            outputs = self._model.generate(**inputs, **self._generation_args)

        response = self._tokenizer.decode(outputs[0], skip_special_tokens=False)
        match = re.search(r"<think>(.*?)</think>(.*)", response, re.DOTALL)

        if match:
            reasoning = match.group(1).strip().replace("<think>", "")
            answer = match.group(2).strip().replace("<|end_of_text|>", "")
        else:
            reasoning = ""
            answer = (
                response.split("<|assistant|>")[-1]
                .replace("<think>", "")
                .replace("</think>", "")
                .replace("<|end_of_text|>", "")
            )

        return reasoning, answer

    def _generate_sagemaker(self, user_prompt: str) -> tuple[str, str]:
        payload = {
            "messages":    [{"role": "user", "content": user_prompt}],
            "temperature": self.temperature,
            "max_tokens":  self.max_tokens,
        }
        response = self._sagemaker_runtime.invoke_endpoint(
            EndpointName=self._endpoint_name,
            Body=json.dumps(payload),
            ContentType="application/json",
        )
        body = json.loads(response["Body"].read().decode("utf-8"))
        return self._extract_reasoning_from_message(body["choices"][0]["message"])

    def _generate_baseten(self, user_prompt: str) -> tuple[str, str]:
        data = {
            "messages":    [{"role": "user", "content": user_prompt}],
            "max_tokens":  self.max_tokens,
            "temperature": self.temperature,
        }
        response = requests.post(
            self._endpoint_url,
            headers={"Authorization": f"Api-Key {self._api_key}"},
            json=data,
        )
        response.raise_for_status()
        body = response.json()
        return self._extract_reasoning_from_message(body["choices"][0]["message"])

    def _generate_bedrock(self, user_prompt: str) -> tuple[str, str]:
        body = {
            "messages":    [{"role": "user", "content": user_prompt}],
            "max_tokens":  self.max_tokens,
            "temperature": self.temperature,
        }
        response = self._bedrock_runtime.invoke_model(
            modelId=self._model_arn,
            body=json.dumps(body),
        )
        response_body = json.loads(response["body"].read())
        raw_generation = response_body["choices"][0]["message"]["content"]
        return self._parse_bedrock_reasoning(raw_generation)