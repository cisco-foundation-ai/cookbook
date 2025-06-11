# Frequently Asked Questions

### Q: Where can we find the Foundation AI models?
You can download the released models from our [Hugging Face page](https://huggingface.co/fdtn-ai), where model cards for each model are also available.
To access preview models, such as the reasoning model, please request early access via [this form](https://fdtn.ai/early-access).

### Q: Can we use the models for commercial purposes free of charge?
Yes! Our models are licensed under Apache 2.0, allowing free commercial use as long as you comply with the license terms.

### Q: Are GPUs required to run the models?
Technically, no. However, for practical purposes, we recommend using GPUs for faster inference.
In CPU-only environments, we suggest using quantized models for optimal performance. See [the quantization section](https://github.com/RobustIntelligence/foundation-ai-cookbook/tree/main/3_adoptions/quantization) for more details.

### Q: How are LLMs being adopted in cybersecurity today?
LLMs are used in two main ways:
- To **augment security products**—embedding capabilities like alert summarization, detection enrichment, and threat simulation.
- To build **custom, end-to-end security workflows** internally—because off-the-shelf products often don’t meet evolving needs.
These internal workflows are becoming common across SOCs and security engineering teams as organizations push toward AI-native operations.

### Q: What are the most common use cases for LLMs in cybersecurity?
Three high-value areas have emerged:
- **SOC acceleration**: Automating alert triage, summarizing incidents, and drafting case notes.
- **Proactive threat defense**: Simulating attacks, mapping TTPs, and prioritizing vulnerabilities.
- **Engineering enablement**: Reviewing code for security issues, validating configs, and compiling compliance evidence.
See [examples section](https://github.com/RobustIntelligence/foundation-ai-cookbook/tree/main/2_examples) for sample codes implementing the cybersecurity use cases.

### Q: What does the Foundation AI base model do differently?
The Foundation AI model:
- Is an **8B parameter model pre-trained entirely on cybersecurity data** (5B tokens, publicly sourced).
- Can be **fine-tuned more effectively** thanks to its domain alignment, and in addition we provide tools for fine-tuning so that analysts without expertise can easily fine-tune models.
- Is compact and performant enough to **deploy in constrained environments (1–2 A100s)**.
To learn more, refer to the model's [technical report](https://arxiv.org/abs/2504.21039).

### Q: Do the performance gains really matter?
Yes! Even modest gains are significant:
- On benchmarks like CTI-MCQA and CTI-RCM, the Foundation model is **3–6% better than Llama 3.1 8B**.
- Outperforms **Llama-3.1 8B** and **matches/exceeds Llama-3.1 70B** on domain-specific benchmarks.
- These results were achieved **without proprietary data**—only public, open-source cybersecurity content.
- For fine-tuned use cases like **MITRE ATT&CK extraction**, the model outperformed Llama 3.1 7B by **10%+**, a margin that often determines **deploy or not deploy** decisions in real-world use.

| **Benchmark** | **Foundation AI Base Model** | **Llama-3.1-8b**  | **Llama-3.1 70B** |
| --- | --- | --- | --- |
| [CTI-MCQA](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5acd3c628aa1819fbf07c39ef73e7285-Abstract-Datasets_and_Benchmarks_Track.html) | 67.95 | 64.14 | 68.23 |
| [CTI-RCM](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5acd3c628aa1819fbf07c39ef73e7285-Abstract-Datasets_and_Benchmarks_Track.html) | 73.37 | 66.43 | 72.66 |

### Q: Can’t we just fine-tune GPT-4 or Claude instead?
There are **significant limitations** to fine-tuning proprietary models:
- **Higher cost**: Fine-tuning GPT-4.1 is ~1.5× the price of standard **inference**.
- **Lack of control**: Model versions change frequently; fine-tunes can break or become deprecated.
- **No architectural extensibility**: You **can’t build on top of closed-source models**—e.g., creating a classifier head is impossible because you **don’t have access to intermediate activations**. This makes tasks like supervised classification or structured predictions infeasible. You’re restricted to “prompt-and-predict” APIs, limiting use cases and custom architecture development.
- **Proprietary Data and Deployment complexity**: Most customers require **in-VPC or on-premise deployment**, which proprietary APIs do not allow.
- **Customer resistance**: Many security teams explicitly refuse to use tools relying on 3rd-party APIs for inference.
