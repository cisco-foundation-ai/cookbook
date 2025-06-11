"""
The `Model` class is an interface between the ML model that you're packaging and the model
server that you're running it on.

The main methods to implement here are:
* `load`: runs exactly once when the model server is spun up or patched and loads the
   model onto the model server. Include any logic for initializing your model, such
   as downloading model weights and loading the model into memory.
* `predict`: runs every time the model server is called. Include any logic for model
  inference and return the model output.

See https://truss.baseten.co/quickstart for more.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict


def get_default_generation_args(tokenizer):
    return {
        "max_new_tokens": 256,
        "temperature": None,
        "repetition_penalty": 1.2,
        "do_sample": False,
        "use_cache": True,
        "eos_token_id": tokenizer.eos_token_id,
        "pad_token_id": tokenizer.pad_token_id,
    }

class Model:
    def __init__(self, **kwargs):
        self.model_name = kwargs["config"]["model_metadata"]["repo_id"]


    def load(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )


    def predict(self, request: Dict):
        prompt = request.pop("prompt")
        generation_args = get_default_generation_args(self.tokenizer)
        generation_args.update(request.pop("generate_args", {}))

        # device is hard-coded to cuda as A100 is used (see config.yaml)
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **generation_args,
            )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"output": response}
