# Quantization

Quantization reduces inference computational and memory demands by encoding weights and activations with lower-precision data types, enabling models to run practically on devices without GPUs.

We have released two quantized versions of our [base model](https://huggingface.co/fdtn-ai/Foundation-Sec-8B) as well as one quantized version of our [instruct model](https://huggingface.co/fdtn-ai/Foundation-Sec-8B-Instruct):
- [fdtn-ai/Foundation-Sec-8B-Q4_K_M-GGUF](https://huggingface.co/fdtn-ai/Foundation-Sec-8B-Q4_K_M-GGUF): 4-bit quantized (~4.92GB memory footprint)
- [fdtn-ai/Foundation-Sec-8B-Q8_0-GGUF](https://huggingface.co/fdtn-ai/Foundation-Sec-8B-Q8_0-GGUF): 8-bit quantized (~8.54GB memory footprint)
- [fdtn-ai/Foundation-Sec-8B-Instruct-Q8_0-GGUF](https://huggingface.co/fdtn-ai/Foundation-Sec-8B-Instruct-Q8_0-GGUF): 8-bit quantized instruct (~8.54GB memory footprint)

Refer to [the sample code](https://github.com/RobustIntelligence/foundation-ai-cookbook/blob/main/3_adoptions/quantization/quantization.ipynb) to run these quantized models.

Additionally, the Hugging Face community has quantized our models. For example, access the qualtized models [here](https://huggingface.co/models?other=base_model%3Aquantized%3Afdtn-ai%2FFoundation-Sec-8B) built from base models.
