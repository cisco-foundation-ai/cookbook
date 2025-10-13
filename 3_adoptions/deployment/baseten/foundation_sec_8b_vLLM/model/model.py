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
        "max_new_tokens": 1024,
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
        messages = request.pop("messages")
        generation_args = get_default_generation_args(self.tokenizer)
        generation_args.update(request.pop("generate_args", {}))

        # device is hard-coded to cuda as A100 is used (see config.yaml)
        model_inputs = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(model_inputs, return_tensors="pt", add_special_tokens=False)
        input_ids = inputs["input_ids"].to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                **generation_args,
            )
        
        response = self.tokenizer.decode(outputs[0][input_ids.shape[1]:],  # Only get new tokens
                                         skip_special_tokens = False)
        
        if response.endswith(self.tokenizer.eos_token):
            response = response[:-len(self.tokenizer.eos_token)]

        return {"output": response}