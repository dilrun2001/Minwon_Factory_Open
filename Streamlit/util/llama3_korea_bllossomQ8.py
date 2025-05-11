# (이미 설치하셨으니 생략 가능)

# HF 허브에서 GGUF 파일만 내려받기
def useAi(minwon,answer,answer_format):
    from huggingface_hub import hf_hub_download

    model_path = hf_hub_download(
        repo_id="QuantFactory/llama-3-Korean-Bllossom-8B-GGUF",
        filename="llama-3-Korean-Bllossom-8B.Q8_0.gguf"
    )

    # llama-cpp-python 으로 모델 로드 및 생성 함수 정의
    from llama_cpp import Llama

    llm = Llama(
        model_path=model_path,
        n_gpu_layers=-1,  # GPU 전체 사용
        n_ctx=4096,
        chat_format="chatml",  # 또는 "llama-3" 등 모델에 맞게 설정
    )

    messages = [
        {"role": "system", "content": """당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
         기관 이름은 '사하구청'입니다.
         
         답변은 **아래 템플릿 형식을 정확히 지켜서** 작성해주세요.
         템플릿을 벗어나는 내용은 작성하지 마세요.
         출력 시작 부분에 공백이나 들여쓰기를 넣지 말고, 문장 맨 앞에서 바로 시작해 주세요.

         ※ [민원 내용]를 요약하여 정중한 행정 문서 문체로, [답변 템플릿]을 참고하여 [민원 요지]가 들어간 항목을 [민원요지]와 함께 부드럽게 이어지도록 수정해주세요.
         ※ [답변 요지]를 파악하여 정중한 행정 문서 문체로, [답변 템플릿]을 참고하여 [답변 요지]를 작성해주세요.
         (예: '~로 확인되어 조치 중입니다.', '~한 점 양해 부탁드립니다.' 등)
         
         """},

        {"role": "user", "content": """
     
         다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

         [민원 내용]
         """+minwon+"""
         
         [답변 요지]
         """+answer+"""

         [답변 템플릿]
         """+answer_format}
    ]

    output = llm.create_chat_completion(
        messages=messages,
        temperature=0.6,
        top_p=0.9,
        max_tokens=512,
    )

    print(output['choices'][0]['message']['content'])
    return output['choices'][0]['message']['content']  #output['choices'][0]['message']['content']

