from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
import torch

# === 설정 ===
model_name = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
data_path = "QAdata.jsonl"
output_dir = "./llama3-ko-munwon-finetuned-full"

# === 데이터 불러오기 ===
dataset = load_dataset("json", data_files=data_path, split="train")

# === 토크나이저 & 모델 로딩 ===
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token  # padding 문제 방지

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"  # GPU 자동 할당
)

# === 전처리 ===
def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=512,
    )

tokenized_dataset = dataset.map(tokenize, batched=True)

# === 데이터로더 ===
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# === 학습 설정 ===
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=10,
    gradient_accumulation_steps=4,
    num_train_epochs=5,
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
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
