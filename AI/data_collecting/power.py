# run_llama3_windows.py

"""
Windows 11, NVIDIA RTX 2080 Super (CUDA 11+) 환경에서
MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M 모델을
로컬 GPU로 로드하고 추론하는 통합 스크립트입니다.
"""

# 0) (최초 1회만) 라이브러리 설치
# --------------------------------
# PowerShell에서 아래를 한 번 실행하세요:
# pip install --upgrade pip
# pip install transformers accelerate torch bitsandbytes llama-cpp-python huggingface_hub

import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# 1) 모델 다운로드 (Hugging Face 캐시에 저장)
# -------------------------------------------
print("모델 다운로드 중… (최초 1회만 시간이 걸려요)")
model_path = hf_hub_download(
    repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
    filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf"
)
print(f"모델이 다운로드되어 저장되었습니다:\n  {model_path}\n")

# 2) Llama-CPP-Python으로 모델 로드
# ---------------------------------
print("모델 로드 중…")
llm = Llama(
    model_path=model_path,
    n_ctx=2048,          # 최대 컨텍스트 길이
    temperature=0.6,     # 창의성(0.0~1.0)
    top_p=0.9,           # nucleus sampling
    device="cuda:0",     # RTX 2080 Super (GPU 0) 사용
    n_gpu_layers=32      # 가능한 모든 레이어를 GPU에서 계산
)
print("모델 로드 완료!\n")

# 3) 추론 함수 정의
# -----------------
def generate(prompt: str, max_tokens: int = 512):
    """
    주어진 prompt를 바탕으로 max_tokens 만큼 생성하고,
    "<|eot_id|>" 토큰에서 멈춥니다.
    """
    resp = llm(
        prompt=prompt,
        max_tokens=max_tokens,
        stop=["<|eot_id|>"]
    )
    return resp["choices"][0]["text"]

# 4) 메인: 예시 프롬프트로 테스트
# -------------------------------
if __name__ == "__main__":
    PROMPT = """You are a helpful AI assistant. Please answer the user's questions kindly.
당신은 유능한 AI 어시스턴트 입니다. 사용자의 질문에 대해 친절하게 답변해주세요."""

    instruction = """
당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
다음은 민원에 대한 '답변 요지'입니다.
해당 내용을 바탕으로 정중하고 행정 형식에 맞는 '회신문'을 작성해주세요.

[답변 요지]
○ 부산시와의 협의를 통해 버스 배차간격 조정 논의
○ 예산상의 문제로 불가능할수도 있음

[회신문]
"""
    full_prompt = PROMPT + "\n" + instruction

    print("추론 시작…")
    result = generate(full_prompt, max_tokens=512)
    print("\n===== 생성된 회신문 =====\n")
    print(result.strip())