# 1. Quickstarts
Guides to quickly download and use models for introductory topics.
For each model, there's a demo notebook for quick start.

## Models
The models can be run on a single Nvidia A100 GPU.
<Released>
- [Base Model (Foundation-Sec-8B)](https://github.com/RobustIntelligence/foundation-ai-cookbook/blob/main/1_quickstarts/Quickstart_Foundation-Sec-8B.ipynb)

<preview mode>
- [Instruct Model (instruction-finetuned model)](https://github.com/RobustIntelligence/foundation-ai-cookbook/blob/main/1_quickstarts/Preview_Quickstart_instruct_model.ipynb)
- [Reasoning Model](https://github.com/RobustIntelligence/foundation-ai-cookbook/blob/main/1_quickstarts/Preview_Quickstart_reasoning_model.ipynb)

**Interested in preview-mode models? Request early access using the [form](https://fdtn.ai/early-access)!**

## Pre-requisites
Python Packages
- transformers
- torch

Additionally, if the quantized models are used:
- llama-cpp-python
- huggingface_hub
For more details about the quantized models, see [the section of quantization](https://github.com/RobustIntelligence/foundation-ai-cookbook/tree/main/3_adoptions/quantization).
