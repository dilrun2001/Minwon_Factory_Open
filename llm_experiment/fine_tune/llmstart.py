from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# ✅ 모델 경로
model_path = "./llama3-ko-munwon-finetuned"  # 너가 학습 후 저장한 폴더

# ✅ GPU 확인
device = "cuda" if torch.cuda.is_available() else "cpu"

# ✅ 토크나이저 및 모델 로드
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path).to(device)

# ✅ 텍스트 생성 파이프라인 생성
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device == "cuda" else -1,  # GPU 사용
)

# ✅ 테스트 프롬프트
prompt = "부산시 대중교통 관련 민원이 접수된 경우,"
result = generator(
    prompt,
    max_new_tokens=300,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id  # padding 문제 방지
)

# ✅ 출력
print(result[0]['generated_text'])
