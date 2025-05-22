# (이미 설치하셨으니 생략 가능)

# HF 허브에서 GGUF 파일만 내려받기
def AI_print_answer(minwon,answer,answer_format):
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
        chat_format="llama-3",  # 또는 "llama-3" 등 모델에 맞게 설정
    )

    messages = [
    {
        "role": "system",
        "content": """당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
기관 이름은 '사하구청'입니다.

다음의 **[답변 템플릿] 형식을 정확히 지켜서** 작성하십시오. 
⚠️ [답변 템플릿]의 형식을 **그대로 유지하고**, 출력 시작 부분이나 끝에 어떠한 추가 설명도 하지 마십시오.

※ 반드시 출력은 [답변 템플릿] 안에 있는 형식을 따르며, 템플릿 외 문장은 추가하지 마십시오.
※ 템플릿 내 `[민원요지]` 부분은 민원 내용을 행정 문서 문체로 정중하게 요약하여 대체하되, `[민원요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
※ 템플릿 내 `[답변요지]` 부분은 답변 요지를 정중하고 행정적인 문체로 바꾸어 넣되, `[답변요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
※ 출력에는 들여쓰기, 불필요한 줄바꿈, 공백 없이 문장 맨 앞에서 바로 시작하십시오.
"""
    },
    {
        "role": "user",
        "content": """
다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

[민원 내용]
""" + minwon + """

[답변 요지]
""" + answer + """

[답변 템플릿]
""" + answer_format
    }
]

    output = llm.create_chat_completion(
        messages=messages,
        temperature=0.6,
        top_p=0.9,
        max_tokens=512,
    )

    print(output['choices'][0]['message']['content'])
    return output['choices'][0]['message']['content']  #output['choices'][0]['message']['content']


def AI_print_minwon_sub(minwon):
    from huggingface_hub import hf_hub_download

    model_path = hf_hub_download(
        repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
        filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf"
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
    {
        "role": "system",
        "content": """당신은 민원 내용을 간결하게 요약하는 요약봇입니다.

        [목표]
        아래 [민원내용]을 읽고, 핵심 내용을 공무원이 빠르게 파악할 수 있도록 **한 줄 또는 두 줄로 요약**해 주세요.

        [출력 형식]
        - 요약문만 출력해 주세요.
        - 접두사 없이, 바로 요약 내용만 작성하세요.
        """
    },
    {
        "role": "user",
        "content": f"""[민원내용]{minwon}
        """
    }
]

    output = llm.create_chat_completion(
        messages=messages,
        temperature=0.6,
        top_p=0.9,
        max_tokens=512,
    )

    print(output['choices'][0]['message']['content'])
    return output['choices'][0]['message']['content']  #output['choices'][0]['message']['content']