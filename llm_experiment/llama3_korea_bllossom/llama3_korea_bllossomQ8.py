# (이미 설치하셨으니 생략 가능)

# HF 허브에서 GGUF 파일만 내려받기
def useAi(answer,answer_format):
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
         
         이 요지를 바탕으로 **아래 템플릿 형식을 정확히 지켜서** [답변내용]을 작성해주세요.

         ※ 특히 [답변요지]를 파악하여 정중하고 행정 문서 문체를 [답변 템플릿] 을 참고하여 작성해주세요. 
         (예: '~로 확인되어 조치 중입니다.', '~한 점 양해 부탁드립니다.' 등)"""},

        {"role": "user", "content": """
     
         다음은 민원에 대한 [답변 요지]입니다.
         
         [답변 요지]
         """+answer+"""

         [답변 템플릿]

         """+answer_format}
    ]

    output = llm.create_chat_completion(
        messages=messages,
        temperature=0.7,
        top_p=0.9,
        max_tokens=512,
    )

    print(output['choices'][0]['message']['content'])  #output['choices'][0]['message']['content']

