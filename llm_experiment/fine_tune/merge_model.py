from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# === 경로 설정 ===
base_model_name = "MLP-KTLim/llama-3-Korean-Bllossom-8B"  # 원본 모델
lora_model_path = "./llama3-ko-minwon-finetuned"         # LoRA 학습 결과 경로
merged_output_path = "./llama3-ko-minwon-merged"         # 병합 후 저장할 경로

# === 원본 모델 로드 ===
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# === LoRA 적용 모델 로드 ===
model = PeftModel.from_pretrained(base_model, lora_model_path)

# === 병합 수행 ===
merged_model = model.merge_and_unload()

# === 저장 ===
merged_model.save_pretrained(merged_output_path)
tokenizer = AutoTokenizer.from_pretrained(base_model_name)
tokenizer.save_pretrained(merged_output_path)

print(f"✅ 병합 완료! 저장 위치: {merged_output_path}")