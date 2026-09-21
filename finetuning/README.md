# Mansam fine-tuning preparation

Status: draft data and a training scaffold, not a trained model.

`prepare_data.py` produces conversational prompt/completion examples from the local catalog, with English and Arabic targets. Facts appear in the input evidence; the target is the JSON shape consumed by the chatbot. Product-name groups are kept separate between train and validation, including size variants.

The existing `ssot-training.jsonl` contains source metadata rather than conversational answer targets, so it is not passed directly to supervised fine-tuning. Existing scripted flows also conflict with the current free-form conversation goal.

Before training, review the generated examples and add real, anonymized multi-turn examples covering interruptions, preference corrections, no-match answers, and quantity constraints. The generated validation set tests unseen products with familiar question templates; it does not establish real conversation quality. This initial dataset trains the answer stage only, not the retrieval planner.

## Training environment

Use a separate CUDA-capable environment with compatible PyTorch, transformers, datasets, accelerate, bitsandbytes, peft and trl packages. These are not added to the website's runtime requirements. The QLoRA scaffold follows current TRL SFTTrainer conventions but has not been executed or GPU-memory-tested. Start with a small smoke run and monitor memory before a full job.

Access to the gated `meta-llama/Llama-3.1-8B-Instruct` weights is required, with the model terms accepted by the account holder and a token authorized to download them. An inference-only token may not provide this access. Do not put credentials in files or source control.

Run preparation with `python finetuning/prepare_data.py`. In the prepared GPU environment, run `python finetuning/train_qlora.py`. Training downloads weights and saves a LoRA adapter locally; nothing is uploaded automatically.

A custom adapter does not change the shared Novita model. To use it in the chatbot, deploy the base model plus adapter to an inference endpoint that supports it and update the backend endpoint/model configuration after evaluation. Keep RAG for current prices, stock, and policies.

References:
- https://huggingface.co/docs/trl/sft_trainer
- https://huggingface.co/docs/trl/peft_integration
- https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
