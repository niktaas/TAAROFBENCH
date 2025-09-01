from predibase import Predibase, FinetuningConfig, DeploymentConfig

# ==== CONFIGURATION ====
API_TOKEN = "your-api-token"
DATASET_PATH = "path/to/sft_data.csv"   
DATASET_NAME = "finetuning_data"
REPO_NAME = "Taarof-Llama3-8b"
REPO_DESCRIPTION = "SFT"
BASE_MODEL = "llama-3-8b-instruct"

# Fine-tuning hyperparameters
EPOCHS = 10
RANK = 16
LEARNING_RATE = 1e-4
ADAPTER_TYPE = "turbo_lora"
TARGET_MODULES = ["q_proj", "v_proj", "k_proj"]

# ==== RUN SCRIPT ====
def main():
    pb = Predibase(api_token=API_TOKEN)

    # Upload the dataset
    print("Uploading dataset to Predibase...")
    dataset = pb.datasets.from_file(DATASET_PATH, name=DATASET_NAME)

    # Create or access a model repo
    print(f"Creating repo: {REPO_NAME}...")
    repo = pb.repos.create(name=REPO_NAME, description=REPO_DESCRIPTION, exists_ok=True)

    # Launch fine-tuning job
    print(" Starting fine-tuning job...")
    adapter = pb.adapters.create(
        config=FinetuningConfig(
            base_model=BASE_MODEL,
            adapter=ADAPTER_TYPE,
            epochs=EPOCHS,
            rank=RANK,
            learning_rate=LEARNING_RATE,
            target_modules=TARGET_MODULES,
            apply_chat_template=False
        ),
        dataset=DATASET_NAME,
        repo=repo,
        description="Fine-tuning with tuned epochs and learning rate for Persian taarof"
    )

    print(" Fine-tuning job submitted.")

if __name__ == "__main__":
    main()
