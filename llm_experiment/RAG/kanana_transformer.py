import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig # 1. BitsAndBytesConfig 추가

# 사용자님이 찾아주신 정확한 모델 ID
model_id = "kakaocorp/kanana-1.5-8b-instruct-2505"

print(f"{model_id} 모델을 로딩 중입니다... (4비트 양자화 적용)")

# 2. 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(model_id)

# -----------------------------------------------------------
# [변경됨] 3. 4비트 양자화 설정 정의
# -----------------------------------------------------------
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,              # 4비트 로딩 활성화
    bnb_4bit_quant_type="nf4",      # 성능이 더 좋은 NF4 포맷 사용
    bnb_4bit_compute_dtype=torch.bfloat16  # 연산은 16비트로 해서 정확도 유지
)

# -----------------------------------------------------------
# [변경됨] 4. 모델 로드 (설정 적용)
# -----------------------------------------------------------
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config, # 위에서 만든 설정 적용
    device_map="auto"                        # GPU 자동 할당
)

# 5. 질문 작성 (Chat 템플릿 사용)
messages = [
    {"role": "system", "content": "당신은 민원담당 공무원입니다. 다음 질문을 보고 어떻게 답변할지 생각하시오 지역명은 적절하게 포함시켜야합니다."},
    {"role": "user", "content": "당리동 14번지 아파트에서 이상한 쾅쾅하는 소리가 나요 해결해주세요"}
]

# 6. 입력 데이터 전처리
input_ids = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt"
).to(model.device)

# 7. 답변 생성
outputs = model.generate(
    input_ids,
    max_new_tokens=1024,
    do_sample=True,
    temperature=0.7,
    repetition_penalty=1.1
)

# 8. 결과 디코딩 및 출력
response = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)

print("\n[카나나 답변]")
print(response)