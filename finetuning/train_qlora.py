"""QLoRA training entrypoint. Requires a separately configured CUDA environment."""
import os
from pathlib import Path


def main():
    import torch
    from datasets import load_dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, prepare_model_for_kbit_training
    from trl import SFTTrainer, SFTConfig

    if not torch.cuda.is_available():
        raise RuntimeError('A working CUDA PyTorch environment is required.')
    model_id = 'meta-llama/Llama-3.1-8B-Instruct'
    root = Path(__file__).resolve().parent
    env_file = root.parent / '.env'
    if env_file.is_file() and 'HF_TOKEN' not in os.environ:
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line.startswith('HF_TOKEN='):
                os.environ['HF_TOKEN'] = line.partition('=')[2].strip().strip('"\'')
    token = os.environ.get('HF_TOKEN')
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id, token=token, device_map={'': 0},
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16))
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    data = load_dataset('json', data_files={
        'train': str(root / 'data/train.jsonl'), 'validation': str(root / 'data/validation.jsonl')})
    trainer = SFTTrainer(model=model, processing_class=tokenizer,
        train_dataset=data['train'], eval_dataset=data['validation'],
        peft_config=LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05,
            target_modules=['q_proj', 'v_proj'], task_type='CAUSAL_LM'),
        args=SFTConfig(output_dir=str(root / 'checkpoints'), max_length=1024,
            per_device_train_batch_size=1, per_device_eval_batch_size=1,
            gradient_accumulation_steps=8, gradient_checkpointing=True,
            learning_rate=1e-4, num_train_epochs=1,
            max_steps=int(os.environ.get('MANSAM_TRAIN_STEPS', '-1')), fp16=True, bf16=False,
            completion_only_loss=True, eval_strategy='epoch', save_strategy='epoch',
            report_to='none', push_to_hub=False, logging_steps=5))
    trainer.train()
    trainer.save_model(str(root / 'Llama-Mansam-adapter'))
    tokenizer.save_pretrained(str(root / 'Llama-Mansam-adapter'))


if __name__ == '__main__':
    main()
