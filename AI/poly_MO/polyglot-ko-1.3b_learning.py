## 구글 코랩 기준 코드
# ✅ 1. 필수 패키지 설치
!pip install transformers peft datasets accelerate bitsandbytes

# ✅ 2. Hugging Face 로그인 (이미 했다면 생략)
from huggingface_hub import login
login("")  # 여기에 본인ㄴㄴㄴ 토큰 넣기

# ✅ 3. 구글 드라이브 마운트 (학습 데이터 불러오기 용도)
from google.colab import drive
drive.mount('/content/drive')

# ✅ 4. 모델 & 토크나이저 불러오기
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig, TaskType

base_model = "EleutherAI/polyglot-ko-1.3b"

tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="auto",
    torch_dtype="auto"
)

# ✅ 5. LoRA 설정
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["query_key_value", "dense_h_to_4h", "dense_4h_to_h"],  # GPTNeoX 모델에 맞게 수정
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)

# ✅ 6. 데이터 로딩 및 전처리
from datasets import load_dataset

dataset = load_dataset("json", data_files="/content/drive/MyDrive/final_cleaned_v3.jsonl")["train"]

def format_prompt(example):
    prompt = f"민원 내용:\n{example['instruction']}\n\n답변:\n{example['output']}"
    tokenized = tokenizer(
        prompt,
        truncation=True,
        padding="max_length",
        max_length=512
    )
    return {
        "input_ids": tokenized["input_ids"],
        "attention_mask": tokenized["attention_mask"],
        "labels": tokenized["input_ids"]
    }

tokenized_dataset = dataset.map(format_prompt, remove_columns=dataset.column_names)

# ✅ 7. 학습 설정
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling

training_args = TrainingArguments(
    output_dir="./polyglot-ko-minwon-model",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    learning_rate=2e-5,
    logging_steps=10,
    save_steps=100,
    evaluation_strategy="steps",
    eval_steps=50,
    save_total_limit=2,
    report_to="none",
    logging_dir="./logs"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset.select(range(50)),  # 작은 검증용 셋
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# ✅ 8. 학습 시작
trainer.train()