import transformers
import torch
import time
#일반 버전
#model_id = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
#model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M'

# Adjusted for M3 MacBook compatibility
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.float16},  # use float16 instead of bfloat16
    device_map="auto"
)

pipeline.model.eval()

PROMPT = '''You are a helpful AI assistant. Please answer the user's questions kindly. 당신은 유능한 AI 어시스턴트 입니다. 사용자의 질문에 대해 친절하게 답변해주세요.'''
instruction = """
당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
다음은 민원에 대한 '답변 요지'입니다.
해당 내용을 바탕으로 정중하고 행정 형식에 맞는 '회신문'을 작성해주세요.


[답변 요지]
○ 부산시와의 협의를 통해 버스 배차간격 조정 논위
○ 예산상의 문제로 불가능할수도 있음

[회신문]
"""

messages = [
    {"role": "system", "content": f"{PROMPT}"},
    {"role": "user", "content": f"{instruction}"}
    ]

prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

start_time = time.time()
outputs = pipeline(
    prompt,
    #max_new_tokens=2048,
    max_new_tokens=512,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9
)

print(outputs[0]["generated_text"][len(prompt):])
end_time = time.time()
print(f"⏱️ 생성 소요 시간: {end_time - start_time:.2f}초")
