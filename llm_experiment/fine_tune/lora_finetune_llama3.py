from datasets import load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer, 
    default_data_collator
)
from peft import get_peft_model, LoraConfig, TaskType
import torch

# === 설정 ===
model_name = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
data_path = "QAdata.jsonl"
output_dir = "./llama3-ko-minwon-finetuned"
max_seq_length = 2048  # 시퀀스 최대 길이

# === 데이터 불러오기 ===
dataset = load_dataset("json", data_files=data_path, split="train")

# === 토크나이저 & 모델 로딩 ===
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token  # pad_token 미설정 방지

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,  # bf16 사용
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

# === Llama 3 채팅 템플릿 설정 ===
tokenizer.chat_template = """
{%- for message in messages -%}
    {%- if message['role'] == 'system' -%}
        {{- '<|begin_of_text|>' + message['content'] + '<|eot_id|>' -}}
    {%- elif message['role'] == 'user' -%}
        {{- '<|start_header_id|>user<|end_header_id|>\n\n' + message['content'] + '<|eot_id|>' -}}
    {%- elif message['role'] == 'assistant' -%}
        {{- '<|start_header_id|>assistant<|end_header_id|>\n\n' + message['content'] + '<|eot_id|>' -}}
    {%- endif -%}
{%- endfor -%}
"""

# === 전처리 함수 ===
def preprocess(example):
    # 대화 형식 구성
    messages = [
        {"role": "user", "content": f"""[민원 내용]
{example['instruction']}

[답변 요지]
{example['answer']}"""},
        {"role": "assistant", "content": example['output']}
    ]
    
    # chat_template을 사용하여 프롬프트 생성
    full_text = tokenizer.apply_chat_template(messages, tokenize=False)
    
    # 토큰화
    tokenized = tokenizer(
        full_text,
        truncation=True,
        padding="max_length",
        max_length=max_seq_length,
    )

    # 레이블 생성 (Assistant의 답변 부분만 학습)
    labels = tokenized["input_ids"].copy()
    
    # User 프롬프트 부분은 loss 계산에서 제외
    # Assistant 응답 시작점을 찾기 위해 assistant<|end_header_id|>\n\n 부분을 찾음
    assistant_prompt = tokenizer.apply_chat_template([messages[0]], tokenize=False) # User 부분만 템플릿 적용
    assistant_header = "<|start_header_id|>assistant<|end_header_id|>\n\n"
    
    # User + Assistant 헤더까지의 텍스트
    prompt_text = assistant_prompt + assistant_header
    
    # 해당 텍스트를 토큰화하여 길이 계산
    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    prompt_len = len(prompt_ids)

    # prompt 부분의 레이블을 -100으로 설정
    labels[:prompt_len] = [-100] * prompt_len

    tokenized["labels"] = labels
    return tokenized

tokenized_dataset = dataset.map(preprocess, batched=False)

# === Data Collator (기본 패딩 처리) ===
data_collator = default_data_collator

# === 학습 설정 ===
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=5e-5,
    bf16=True,              # A6000 지원됨
    fp16=False,             # bf16과 fp16 동시 사용 금지
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
