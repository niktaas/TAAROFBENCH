import torch
from datasets import load_from_disk
from unsloth import FastLanguageModel, PatchDPOTrainer, is_bfloat16_supported
from transformers import TrainingArguments
from trl import DPOTrainer, DPOConfig

# ========== CONFIGURATION ==========
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
DPO_DATA_PATH = "path/to/dpo_dataset"  
OUTPUT_DIR = "outputs/dpo_llama3"
LOAD_IN_4BIT = True
MAX_SEQ_LENGTH = 2048
USE_GRADIENT_CHECKPOINTING = "unsloth"

# PEFT / LoRA settings
LORA_CONFIG = {
    "r": 16,
    "lora_alpha": 16,
    "lora_dropout": 0,
    "bias": "none",
    "target_modules": [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    "use_rslora": False,
    "loftq_config": None,
    "use_gradient_checkpointing": USE_GRADIENT_CHECKPOINTING,
    "random_state": 3407,
}

# Training settings
TRAINING_ARGS = DPOConfig(
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    warmup_ratio=0.1,
    num_train_epochs=3,
    learning_rate=5e-5,
    fp16=not is_bfloat16_supported(),
    bf16=is_bfloat16_supported(),
    logging_steps=1,
    optim="adamw_8bit",
    weight_decay=0.0,
    lr_scheduler_type="linear",
    seed=42,
    output_dir=OUTPUT_DIR,
    report_to="none"
)

# ========== MAIN PIPELINE ==========
def main():
    print("Loading base model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=LOAD_IN_4BIT
    )

    print("Applying LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model=model,
        **LORA_CONFIG
    )

    print("Loading DPO dataset...")
    dpo_dataset = load_from_disk(DPO_DATA_PATH)

    PatchDPOTrainer()

    print("Starting DPO training...")
    trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=TRAINING_ARGS,
        beta=0.1,
        train_dataset=dpo_dataset,
        tokenizer=tokenizer,
        max_length=1024,
        max_prompt_length=512,
    )

    trainer.train()
    print("DPO training completed and saved to:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
