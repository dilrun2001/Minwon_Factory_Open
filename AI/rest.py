from llama_cpp import Llama

# 모델 경로
model_path = "/Users/cheonjaehyeog/Desktop/llama_models/your_model.gguf"

# 모델 로드
llm = Llama(
    model_path=model_path,
    n_ctx=4096,
    chat_format="chatml",
    n_gpu_layers=0  # 맥북이면 GPU 없이 CPU 사용 가능
)

messages = [
    {"role": "system", "content": "너는 친절한 비서야"},
    {"role": "user", "content": "오늘 뭐 먹을까?"}
]

try:
    output = llm.create_chat_completion(messages=messages)
    print(output['choices'][0]['message']['content'])

except RuntimeError as e:
    if "llama_decode returned -3" in str(e):
        print("디코딩 오류! 캐시 리셋 후 재시도!")
        llm.reset()
        output = llm.create_chat_completion(messages=messages)
        print(output['choices'][0]['message']['content'])