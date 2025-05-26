from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import pandas as pd
from sqlalchemy import create_engine
import os
import shutil
from Streamlit.util.llama3_korea_bllossomQ8 import AI_print_answer, AI_print_minwon_sub


# 1) MySQL에서 민원 데이터 가져와서 Chroma DB 만들기 ========================
# (한 번만 실행하면 됨)
engine = create_engine("mysql+pymysql://root:1234@localhost/minwon")
query = "SELECT answer_yogi,response FROM history"
df = pd.read_sql(query, engine)

# 기존 DB 폴더가 있으면 깨끗하게 삭제
if os.path.exists("minwon_chroma_db/chroma_db"):
    shutil.rmtree("minwon_chroma_db/chroma_db")

# 임베딩 모델 세팅
embedding_model = HuggingFaceEmbeddings(
    model_name="snunlp/KR-SBERT-V40K-klueNLI-augSTS" #서울쪽 모델
)

# 문서 리스트로 변환
docs = []
for _, row in df.iterrows():
    content = f"""
{row["answer_yogi"]}


"""
    docs.append(Document(
        page_content=content.strip(),
        metadata={
            "response": row["response"],
        }
    ))
# Chroma DB 생성 및 저장
chroma_db = Chroma.from_documents(
    docs,
    embedding_model,
    persist_directory="minwon_chroma_db/chroma_db"

)

# 2) LLaMA 양자화 모델 로딩 ===============================================
model_path = hf_hub_download(
    repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
    filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf"
)
llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    temperature=0.6,
    top_p=0.9,
    gpu_layers=-1, # 모든 레이어를 GPU에서
    verbose=False
)


def llama_generate(prompt: str, max_tokens: int = 500) -> str:
    res = llm(prompt=prompt, max_tokens=max_tokens, stop=["<|eot_id|>"])
    return res["choices"][0]["text"]


# 3) 유사 민원 검색 + LLaMA 회신문 생성 함수 =================================
def respond_with_memory(minwon_text: str, innput_answer_yogi: str, k: int = 1):
    # 0) chroma 미 참조하고 그냥 출력 하는 프롬트트 버전 입니다.
    minwon_summary = AI_print_minwon_sub(minwon_text).strip()

    naive_prompt = f"""
You are a 전문 공무원 AI 어시스턴트입니다.

다음 [템플릿]의 ‘3. 가. 나. 다.’ 부분을  
정중한 행정 문체로 작성하고,  
나머지 형식(1·2·4)은 그대로 유지해 주세요.

[템플릿]
1. 안녕하십니까? 귀하께서 국민신문고를 통해 신청하신 민원에 대한 검토 결과를 다음과 같이 알려드립니다.

2. 귀하께서 제출하신 민원의 내용은 {minwon_summary} 에 관한 것으로 이해(또는 판단)됩니다.

3. 
가. {innput_answer_yogi}  
나.  
다.  

4. 답변 내용에 대한 추가 설명이 필요한 경우 △△△부 ○○○과 홀길동 사무관(☎044-200-0000)에게 연락주시면 친절히 안내해 드리겠습니다. 감사합니다.


"""
    print('1단계 출력 중입니다')
    #naive_reply = llama_generate(naive_prompt, max_tokens=300) # 위의 프롬포트를 활용해서 반환을 한다.

    ### 위의 naive_reply 부분을 반환하다.

    # Chroma DB 로드 (persist된)
    db = Chroma(
        persist_directory="minwon_chroma_db/chroma_db",
        embedding_function=embedding_model

    )
    # 1) 유사 민원 검색 (score 포함) 및 필터링
    results = db.similarity_search_with_score(innput_answer_yogi, k=10)

    for doc, dist in results:
        print(f'유사도측정{dist}')


    threshold = 160.0  # 거리 기준 50 까지 유사 닫변요
    similar_docs = [doc for doc, distance in results if distance <= threshold]


    # 2) 프롬프트에 예시로 추가 어떤 것을 [답변 요지를 example_block 에 넣는다].
    vector_db_fixed_answer = ""
    for doc in similar_docs:
        vector_db_fixed_answer += f"""
    {doc.metadata["response"]}


"""
    # DEBUG: show injected prompt values
    print(f"DEBUG [민원의 핵심 요점]: {minwon_summary}")
    print(f"DEBUG [현재 입력한 답변요지]: {innput_answer_yogi}")
    print(f"DEBUG [기존의 답변 내용]: {vector_db_fixed_answer}")

    # 3) 본 프롬프트 구성 벡터 db 참고해서 답변을 생성한다. 그게 없으면 원본 라마만 답변
    system_msg = """\
당신은 전문 공무원 AI 어시스턴트입니다.
다음 **[답변 템플릿]** 형식을 **정확히** 지켜서, **추가 설명 없이 템플릿 부분만** 출력해 주세요.
탬플릿 부분의 문장 끝에는 반드시 '~하였습니다.' 또는 '~되었습니다.' 형태의 종결어미를 사용해야 합니다.
"""
    if vector_db_fixed_answer.strip():
        # build user message with END sentinel
        user_msg = f"""\
[민원의 핵심 요점]
{minwon_summary}

[현재 입력한 답변요지]
{innput_answer_yogi}

[기존의 답변 내용]
{vector_db_fixed_answer}

[답변 템플릿]
1. 안녕하십니까? 귀하께서 국민신문고를 통해 신청하신 민원에 대한 검토 결과를 다음과 같이 알려드립니다.
2. 귀하께서 제출하신 민원의 내용은 [민원의 핵심 요점] 으로 이해 (또는 판단) 됩니다.
3. 귀하의 민원에 대한 검토 결과는 다음과 같습니다.
가. {innput_answer_yogi}
4. 답변 내용에 대한 추가 설명이 필요하신 경우 △△△부 ○○○과 홍길동 사무관(☎044-200-0000)에게 연락 주시면 안내해 드리겠습니다. 감사합니다.
END
"""

        # perform chat completion
        res = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=300,
            stop=["END"],
        )
        mem_reply = res["choices"][0]["message"]["content"].strip()
    else:
        print("유사 답변 없음")
        mem_reply = "유사 답변 없음"
    return  mem_reply






# 4) 인터랙티브 실행 예시 ================================================
if __name__ == "__main__":
    # 한 번만 실행: 다중행 민원 내용 입력
    print("💬 민원 내용을 입력하세요. 입력을 마치려면 빈 줄에서 엔터를 누르세요:")
    minwon_lines = []
    while True:
        line = input()
        if line == "":
            break
        minwon_lines.append(line)
    minwon_text = "\n".join(minwon_lines).strip()
    if minwon_text.lower() == "exit":
        print("🛑 종료합니다!")
        exit()

    # 단일 행 답변 요지 입력
    innput_answer_yogi = input("💬 답변 요지를 입력하세요: ").strip()
    print('출력 중입니다. 기다려 주세요.')
    mem_reply = respond_with_memory(
        minwon_text=minwon_text,
        innput_answer_yogi=innput_answer_yogi,
        k=1
    )
    print("\n✨ [Chroma 미참조 회신문]:\n")
    #print(naive_reply)
    print("\n✨ [Chroma 참조 회신문]:\n")
    print(mem_reply)
# 프로그램 끝