
from ollama import Client, ResponseError
from util.OLLAMA_HOST_config import OLLAMA_HOST
import util.state_copy as state_util
import streamlit   as st
import util.find_similar as RAG

def SahaAi_request(minwon,answer,answer_format,model_name: str = "gpt-oss:20b"):
    system_prompt = """당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
기관 이름은 '사하구청'입니다.

다음의 **[답변 템플릿] 형식을 정확히 지켜서** 작성하십시오. 
⚠️ [답변 템플릿]의 형식을 **그대로 유지하고**, 출력 시작 부분이나 끝에 어떠한 추가 설명도 하지 마십시오.

※ 반드시 출력은 [답변 템플릿] 안에 있는 형식을 따르며, 템플릿 외 문장은 추가하지 마십시오.
※ 템플릿 내 `[민원요지]` 부분은 민원 내용을 행정 문서 문체로 정중하게 요약하여 대체하되, `[민원요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
※ 템플릿 내 `[답변요지]` 부분은 답변 요지를 정중하고 행정적인 문체로 바꾸어 넣되, `[답변요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
"""
    user_prompt = """
다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

[민원 내용]
""" + minwon + """

[답변 요지]
""" + answer + """

[답변 템플릿]
""" + answer_format
    try:
        client = Client(host=OLLAMA_HOST)
        response = client.chat(
            model= model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
        )
        content = response.get("message", {}).get("content", "")
        st.session_state.saha_count += 1
        print(content)
        return content
    except ResponseError as e:
        print(f"❌ API 오류: {e.error}")
    except Exception as e:
        print(f"❌ 오류: {e}")

def SahaAi_request_sub(minwon,model_name: str = "gpt-oss:20b"):
    system_prompt = """당신은 민원 내용을 간결하게 요약하는 요약봇입니다.

        [목표]
        아래 [민원내용]을 읽고, 핵심 내용을 공무원이 빠르게 파악할 수 있도록 **한 줄 또는 두 줄로 요약**해 주세요.

        [출력 형식]
        - 요약문만 출력해 주세요.
        - 접두사 없이, 바로 요약 내용만 작성하세요.
        """
    user_prompt = f"""[민원내용]{minwon}
        """
    try:
        client = Client(host=OLLAMA_HOST)
        response = client.chat(
            model= model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
        )
        content = response.get("message", {}).get("content", "")
        st.session_state.saha_count += 1
        print(content)
        return content
    except ResponseError as e:
        print(f"❌ API 오류: {e.error}")
    except Exception as e:
        print(f"❌ 오류: {e}")


def AI_print_answer(minwon,answer,answer_format):
    from huggingface_hub import hf_hub_download

    model_path = hf_hub_download(
        repo_id="QuantFactory/llama-3-Korean-Bllossom-8B-GGUF",
        filename="llama-3-Korean-Bllossom-8B.Q8_0.gguf"
        )

    if(st.session_state.model == '기본 모델'):
        model_path = hf_hub_download(
        repo_id="QuantFactory/llama-3-Korean-Bllossom-8B-GGUF",
        filename="llama-3-Korean-Bllossom-8B.Q8_0.gguf"
        )
        #st.session_state.default_count += 1
    elif(st.session_state.model == '민원팩토리 모델'):
        model_path = "./util/llm_models/kanana-1.5-15.7b-a3b-instruct-Q4_K_M.gguf"
        #st.session_state.mf_count += 1

    

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
    st.session_state.default_count += 1
    print(output['choices'][0]['message']['content'])
    return output['choices'][0]['message']['content']  #output['choices'][0]['message']['content']


def AI_RAG_print_answer(minwon,answer,answer_format):
    from huggingface_hub import hf_hub_download

    model_path = hf_hub_download(
        repo_id="QuantFactory/llama-3-Korean-Bllossom-8B-GGUF",
        filename="llama-3-Korean-Bllossom-8B.Q8_0.gguf"
        )

    if(st.session_state.model == '기본 모델'):
        model_path = hf_hub_download(
        repo_id="QuantFactory/llama-3-Korean-Bllossom-8B-GGUF",
        filename="llama-3-Korean-Bllossom-8B.Q8_0.gguf"
        )
        #st.session_state.default_count += 1
    elif(st.session_state.model == '민원팩토리 모델'):
        model_path = "./util/llm_models/kanana-1.5-15.7b-a3b-instruct-Q4_K_M.gguf"
        #st.session_state.mf_count += 1

    model = RAG.load_embedding_model()
    df, embeddings =RAG.load_vector_data()
    results = RAG.search_vector_data(minwon, df, embeddings, model, top_k=1)
    best = results[0]

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
        "content": """# Context (맥락)
당신은 행정 문서 관리 시스템에 탑재된 '개인정보 치환 및 문서 편집 AI'입니다. 당신은 공문서의 원본 형식을 훼손하지 않고 특정 데이터만 수정하는 정밀한 작업을 수행합니다.

# Objective (목표)
두 가지 입력이 주어집니다:
1. [입력1]: 기존 담당자 정보(부서, 이름, 전화번호)가 포함된 민원 답변 문서
2. [입력2]: 교체해야 할 새로운 담당자 정보 (부서명, 이름, 전화번호)가 포함된 답변 템플릿

당신의 목표는 [입력1]의 문서 내용 중 마지막 문단에 위치한 '담당자 정보(부서, 이름, 전화번호)'를 찾아 [입력2]의 개인정보로 **정확히 교체**하는 것입니다.
**중요:** 담당자 정보를 제외한 문서의 나머지 모든 내용(인사말, 민원 요지, 답변 내용 등)은 토씨 하나 바꾸지 않고 **원본 그대로 유지**해야 합니다.

# Style (스타일)
- 엄격한 데이터 처리 스타일 (Strict Data Processing)
- 창작이나 요약을 하지 않는 '복사기(Copier)'와 같은 스타일

# Tone (어조)
- 기계적이고 건조하며 정확함.
- 감정이나 의견을 배제함.

# Audience (청중)
이 결과물은 공무원이 검수할 예정이므로 오타, 서식오류, 줄바꿈이 있더라도 본문서의 형식을 바꾸면 안됩니다.

# Response (응답 형식)
[입력1]의 내용에서 개인정보만 변경된 **완성된 문서 본문**만 출력하십시오.
"변경 완료되었습니다" 또는 "결과물은 다음과 같습니다"와 같이 출력 시작 부분이나 끝에 어떠한 추가 설명도 하지 마십시오.

---
[입력 예시]
[입력1]
1. 귀하의 가정에 행복이 가득하시길 바랍니다.

2. 귀하의 민원내용은 불법주차가 많아 진입시 위험한 상황이 발생하는 사하구청 강변환경공원 입구에 대한 문제에 관한 것으로 이해(또는 판단) 됩니다.

3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

가. 해당 지역에 대해 이동식 단속차량을 통한 주차계도 및 단속을 실시하였습니다.

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 주차관리과(조중현, ☎051-220-4562)에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
감사합니다.
[입력2]
1. 귀하의 가정에 행복이 가득하시길 바랍니다.

2. 귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.

3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

가. [답변내용]

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 산림녹지과(김수빈, ☎051-123-1234)에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 
감사합니다.

[출력 예시]
1. 귀하의 가정에 행복이 가득하시길 바랍니다.

2. 귀하의 민원내용은 불법주차가 많아 진입시 위험한 상황이 발생하는 사하구청 강변환경공원 입구에 대한 문제에 관한 것으로 이해(또는 판단) 됩니다.

3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

가. 해당 지역에 대해 이동식 단속차량을 통한 주차계도 및 단속을 실시하였습니다.

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 산림녹지과(김수빈, ☎051-123-1234)에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
감사합니다.
---"""
    },
    {
        "role": "user",
        "content": f"""
        [입력1]
        {best['response']}

        [입력2]
        {answer_format}"""
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