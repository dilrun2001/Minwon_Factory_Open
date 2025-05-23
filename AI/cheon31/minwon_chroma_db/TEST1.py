from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import pandas as pd
from sqlalchemy import create_engine
import os
import shutil

# 1) MySQL에서 민원 데이터 가져와서 Chroma DB 만들기 ========================
# (한 번만 실행하면 됨)
engine = create_engine("mysql+pymysql://root:1234@localhost/minwon")
query = "SELECT answer_yogi,response FROM history"
df = pd.read_sql(query, engine)

# 기존 DB 폴더가 있으면 깨끗하게 삭제
if os.path.exists("./chroma_db"):
    shutil.rmtree("./chroma_db")

# 임베딩 모델 세팅
embedding_model = HuggingFaceEmbeddings(
    model_name="snunlp/KR-SBERT-V40K-klueNLI-augSTS" #서울쪽 모델
)

# 문서 리스트로 변환
docs = []
for _, row in df.iterrows():
    content = f"""
[답변 요지 ]

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
    persist_directory="./chroma_db"
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
    gpu_layers=-1  # 모든 레이어를 GPU에서
)


def llama_generate(prompt: str, max_tokens: int = 500) -> str:
    res = llm(prompt=prompt, max_tokens=max_tokens, stop=["<|eot_id|>"])
    return res["choices"][0]["text"]


# 3) 유사 민원 검색 + LLaMA 회신문 생성 함수 =================================
def respond_with_memory(innput_answer_yogi: str, k: int = 1):
    # 0) chroma 미 참조하고 그냥 출력 하는 프롬트트 버전 입니다.
    naive_prompt = f"""
You are a 전문 공무원 AI 어시스턴트입니다.

다음 [템플릿]의 ‘3. 가. 나. 다.’ 부분을  
정중한 행정 문체로 작성하고,  
나머지 형식(1·2·4)은 그대로 유지해 주세요.

[템플릿]
1. 안녕하십니까? 귀하께서 국민신문고를 통해 신청하신 민원에 대한 검토 결과를 다음과 같이 알려드립니다.

2. 귀하께서 제출하신 민원의 내용은 특정 내용에 관한 것으로 이해(또는 판단)됩니다.

3. 
가. {innput_answer_yogi}  
나.  
다.  

4. 답변 내용에 대한 추가 설명이 필요한 경우 △△△부 ○○○과 홀길동 사무관(☎044-200-0000)에게 연락주시면 친절히 안내해 드리겠습니다. 감사합니다.

[회신문] 
"""
    print('1단계 출력 중입니다')
    naive_reply = llama_generate(naive_prompt, max_tokens=300) # 위의 프롬포트를 활용해서 반환을 한다.

    ### 위의 naive_reply 부분을 반환하다.

    # Chroma DB 로드 (persist된)
    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding_model
    )
    # 1) 유사 민원 검색
    similar_docs = db.similarity_search(innput_answer_yogi, k=k)


    # 2) 프롬프트에 예시로 추가 어떤 것을 [답변 요지를 example_block 에 넣는다.
    vector_db_fixed_answer = ""
    for doc in similar_docs:
        vector_db_fixed_answer += f"""
    [예시 답변]
    {doc.metadata["response"]}


"""
    # 3) 본 프롬프트 구성 벡터 db 참고해서 답변을 생성한다. .... ㅋ
    prompt = f"""
You are a 공무원 AI 어시스턴트 입니다. 

아래 ‘현재 입력한 답변요지’와 ‘기존의 답변 내용’을 참고하여,
정중한 행정 문체로 회신문을 작성해 주세요.


[현재 입력한 답변요지]
{innput_answer_yogi}

[기존의 답변 내용]
{vector_db_fixed_answer}
"""
    # 4) LLaMA 호출
    print('2단계 출력 중입니다')
    mem_reply = llama_generate(prompt, max_tokens=300)
    return naive_reply, mem_reply


# 4) 인터랙티브 실행 예시 ================================================
if __name__ == "__main__":
    print("💬 답변 요지를 입력하세요 (종료: exit) ")
    while True:
        gist = input(">> ").strip()
        if gist.lower() == "exit":
            print("🛑 종료합니다!")
            break
        print('출력 중입니다. 기다려 주세요.')
        naive_reply, mem_reply = respond_with_memory(gist, k=1)# k 조정하여 참고 민원 답변 내용  참고
        print("\n✨ [Chroma 미참조 회신문]:\n")
        print(naive_reply)

        print("\n✨ [Chroma 참조 회신문]:\n")
        print(mem_reply)
        print("\n" + "=" * 60 + "\n")