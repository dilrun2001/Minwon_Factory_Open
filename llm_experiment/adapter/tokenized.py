from transformers import AutoTokenizer
import json

# 경로를 raw string 또는 슬래시로 변경
tokenizer = AutoTokenizer.from_pretrained("E:/study/Minwon_factory/workspace/Llama-DNA-1.0-8B-Instruct")

tokenized_dataset = []

with open("E:/study/Minwon_factory/workspace/data_collecting/final_lora_dataset100.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        prompt = f"### 질문:\n{data['instruction']}\n\n### 답변:\n{data['output']}"
        tokens = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
        labels = tokens["input_ids"].copy()
        tokens["labels"] = labels
        tokenized_dataset.append(tokens)

# 저장 시 to_dict()로 변환
with open("tokenized_dataset100.jsonl", "w", encoding="utf-8") as f:
    for item in tokenized_dataset:
        json.dump(item.data, f)  # 또는 item.to_dict()
        f.write("\n")
