from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling, default_data_collator
from peft import get_peft_model, LoraConfig, TaskType 
import torch

# === 설정 ===
model_name = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
data_path = "QAdata.jsonl"
output_dir = "./llama3-ko-munwon-finetuned"

# === 데이터 불러오기 ===
dataset = load_dataset("json", data_files=data_path, split="train")

# === 토크나이저 & 모델 로딩 ===
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token  # padding 문제 방지

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

# === LoRA 설정 ===
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, lora_config)

# === 전처리 함수 ===
def preprocess(example):
    prompt = f"민원 내용: {example['instruction']}\n답변: "
    response = example["output"]
    full_text = prompt + response + tokenizer.eos_token

    tokenized = tokenizer(full_text, truncation=True, padding="max_length", max_length=1024)
    input_ids = tokenized["input_ids"]
    labels = input_ids.copy()

    prompt_ids = tokenizer(prompt, truncation=True)["input_ids"]
    prompt_len = len(prompt_ids)

    labels[:prompt_len] = [-100] * prompt_len

    tokenized["labels"] = labels
    return tokenized

tokenized_dataset = dataset.map(preprocess, batched=False)

# data_collator는 기본 패딩만 처리하는 걸로 변경
data_collator = default_data_collator

# === 학습 설정 ===
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=10,
    learning_rate=5e-5,
    fp16=True,
    save_strategy="epoch",
    logging_steps=20,
    save_total_limit=2,
    report_to="none"
)

# === 트레이너 실행 ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

trainer.train()

# === 저장 ===
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
