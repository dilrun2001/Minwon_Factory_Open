from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType
import  datasets

# 1. 모델 로드
model = AutoModelForCausalLM.from_pretrained("E:/study/Minwon_factory/workspace/Llama-DNA-1.0-8B-Instruct", load_in_4bit=True)
tokenizer = AutoTokenizer.from_pretrained("E:/study/Minwon_factory/workspace/Llama-DNA-1.0-8B-Instruct")

# 2. PEFT 설정
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    task_type=TaskType.CAUSAL_LM,
    lora_dropout=0.1
)

model = get_peft_model(model, peft_config)

# 3. 데이터 로드
dataset = datasets.load_dataset("json", data_files="E:/study/Minwon_factory/workspace/data_collecting/tokenized_dataset100.jsonl")

# 4. Trainer 설정
training_args = TrainingArguments(
    output_dir="./lora-adapter",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    logging_dir="./logs",
    save_steps=500,
    save_total_limit=1,
    learning_rate=2e-4,
    fp16=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    tokenizer=tokenizer
)

trainer.train()
model.save_pretrained("./lora-adapter")