# (이미 설치하셨으니 생략 가능)

# HF 허브에서 GGUF 파일만 내려받기
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
    filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf"
)

# llama-cpp-python 으로 모델 로드 및 생성 함수 정의
from llama_cpp import Llama

llm = Llama(
    model_path=model_path,
    n_ctx=2048,      # 컨텍스트 길이
    n_gpu_layers=50,
    temperature=0.6, # 창의성
    top_p=0.9,       # nucleus sampling
    repeat_penalty =1.1,
)

def generate(prompt: str, max_tokens: int = 512):
    resp = llm(prompt=prompt, max_tokens=max_tokens, stop=["<|eot_id|>"])
    return resp["choices"][0]["text"]

# 실행 예시
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
print(generate(full_prompt, max_tokens=512))