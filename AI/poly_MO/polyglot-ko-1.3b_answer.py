from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# base 모델 로드 (Polyglot-ko)
base_model = "EleutherAI/polyglot-ko-1.3b"
tokenizer = AutoTokenizer.from_pretrained(base_model)
base = AutoModelForCausalLM.from_pretrained(base_model, device_map="auto", torch_dtype=torch.float16)

# LoRA 체크포인트 경로 (학습한 최신 경로로 바꿔줘!)
adapter_path = "./polyglot-ko-minwon-model/checkpoint-870"

# 학습된 LoRA 어댑터 적용
model = PeftModel.from_pretrained(base, adapter_path).to("cuda")
model.eval()

# 민원 생성 함수 정의 (RAM 안정화 코드 포함!)
def generate_minwon_reply(instruction, max_new_tokens=200):
    prompt = f"민원 내용:\n{instruction.strip()}\n\n답변:"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():  # 학습 아님, 추론이므로 no_grad 사용!
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    final_reply = output_text.split("답변:")[-1].strip()

    #  메모리 정리!
    del inputs, outputs
    torch.cuda.empty_cache()

    print("📝 입력 프롬프트:\n", prompt)
    print("\n📤 전체 생성 결과:\n", output_text)
    print("\n🤖 최종 추출된 답변:\n", final_reply)

    return final_reply


# ✅ 예시 민원 테스트
test_input = """
하단시장 공영주차장에 불법주차 차량이 많아 진입이 어렵습니다.
단속 및 안내 강화 요청드립니다.
"""

# 🚀 추론 실행 (여러 번 해도 안정!)
generate_minwon_reply(test_input)