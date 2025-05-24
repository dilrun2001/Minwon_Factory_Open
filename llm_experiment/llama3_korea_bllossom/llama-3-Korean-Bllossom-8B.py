# (이미 설치하셨으니 생략 가능)

# HF 허브에서 GGUF 파일만 내려받기
def useAi():
    from huggingface_hub import hf_hub_download

    model_path = hf_hub_download(
        repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B",
        filename="MLP-KTLim/llama-3-Korean-Bllossom-8B"
    )

    # llama-cpp-python 으로 모델 로드 및 생성 함수 정의
    from llama_cpp import Llama

    llm = Llama(
        model_path=model_path,
        n_gpu_layers=-1,  # GPU 전체 사용
        n_ctx=4096,
        chat_format="llama-3",  # 또는 "llama-3" 등 모델에 맞게 설정
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
         ○ 정기적으로 청소를 진행하여 청소 유지  
         ○ 또한 예산을 편성해서 더 나은 청소환경 제공

         [답변 템플릿]

         1. 귀하의 가정에 행복이 가득하시길 바랍니다.

         2. 귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.

         3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

         가. [답변내용]

         4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 교통(김수빈, ☎123-1234-1234)에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
         아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 
          감사합니다.

    """}
    ]

    output = llm.create_chat_completion(
        messages=messages,
        temperature=0.7,
        top_p=0.9,
        max_tokens=512,
    )

    print(output['choices'][0]['message']['content'])  #output['choices'][0]['message']['content']

useAi()

