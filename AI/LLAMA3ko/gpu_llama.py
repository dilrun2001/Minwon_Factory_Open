## 라마 모델 양자화 모델 , 템플릿으로 원하는 답변 뽐아내기,
## 불필요한 답변 생성시 임의적으로 MAX TOCKEN 설정하여 답변양 수 줄어버리기
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
    filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf"
)

from llama_cpp import Llama

# GPU 사용할거니까, gpu_layers=-1 설정해줘야함
llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    temperature=0.6,
    top_p=0.9,
    gpu_layers=-35  # => 모든 레이어를 GPU로
)

def generate(prompt: str, max_tokens: int = 200):
    resp = llm(
        prompt=prompt,
        max_tokens=max_tokens,
        stop=["<|eot_id|>"]
    )
    return resp["choices"][0]["text"]


PROMPT = """You are a helpful AI assistant. Please answer the user's questions kindly.
당신은 유능한 AI 어시스턴트 입니다. 사용자의 질문에 대해 친절하게 답변해주세요."""

instruction = """
당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
다음은 민원에 대한 '답변 요지'입니다.
해당 내용을 바탕으로 정중하고 행정 형식에 맞는 '회신문'을 작성해주세요.

[답변 요지]
○ 정기적으로 청소를 진행하여 청소 유지 
○ 또한 예산을 편성해서 더 나은 청소환경 제공



[회신문]
"""

full_prompt = PROMPT + "\n" + instruction

print(generate(full_prompt, max_tokens=200))