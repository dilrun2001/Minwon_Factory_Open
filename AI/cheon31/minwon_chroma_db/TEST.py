from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import pandas as pd
# import mysql.connector
from sqlalchemy import create_engine
import os
import shutil

# 1) MySQL에서 민원 데이터 가져와서 Chroma DB 만들기 ========================
# (한 번만 실행하면 됨)
engine = create_engine("mysql+mysqlconnector://root:1234@localhost/minwon")
query = "SELECT minwon, response, category FROM history"
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
[민원 내용]
{row["minwon"]}

[답변 내용]
{row["response"]}
"""
    docs.append(Document(
        page_content=content.strip(),
        metadata={
            "minwon": row["minwon"],
            "response": row["response"],
            "category": row["category"] or "기타"
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


def llama_generate(prompt: str, max_tokens: int = 200) -> str:
    res = llm(prompt=prompt, max_tokens=max_tokens, stop=["<|eot_id|>"])
    return res["choices"][0]["text"]


# 3) 유사 민원 검색 + LLaMA 회신문 생성 함수 =================================
def respond_with_memory(answer_gist: str, k: int = 1):
    # 0) LLaMA 단독 호출 (Chroma 미참조)
    naive_prompt = f"""
You are a 전문 공무원 AI 어시스턴트입니다.
기관 이름: 사하구청

아래 템플릿 없이, 주어진 답변 요지로 간단히 회신문을 작성해주세요.

[새 민원 답변 요지]
{answer_gist}

[회신문]
"""
    naive_reply = llama_generate(naive_prompt, max_tokens=300)

    # Chroma DB 로드 (persist된)
    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding_model
    )
    # 1) 유사 민원 검색
    similar_docs = db.similarity_search(answer_gist, k=k)

    # 디버깅: 어떤 유사 민원이 선택되었는지 출력
    print(f"🔍 입력 요지: {answer_gist}")
    print(f"🔍 유사 민원 {len(similar_docs)}건 발견:")
    for idx, doc in enumerate(similar_docs, start=1):
        print(f"[{idx}] 예시 답변: {doc.page_content}")

    # 2) 프롬프트에 예시로 추가
    example_blocks = ""
    for doc in similar_docs:
        example_blocks += f"""
[예시 답변]
{doc.page_content}


"""
    # 3) 본 프롬프트 구성
    prompt = f"""
You are a 전문 공무원 AI 어시스턴트입니다.
기관 이름: 사하구청

아래 예시를 참고하여, 주어진 답변 요지로 정중하고 행정 문서 어투의 회신문을 작성해주세요. 이떄 템플릿 부분은 참고하지 말고,
답변요지만을 참고하세요.

{example_blocks}
[새 민원 답변 요지]
{answer_gist}

[회신문]
"""
    # 4) LLaMA 호출
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
        naive_reply, mem_reply = respond_with_memory(gist, k=1)# k 조정하여 참고 민원 답변 내용  참고
        print("\n✨ [Chroma 미참조 회신문]:\n")
        print(naive_reply)
        print("\n✨ [Chroma 참조 회신문]:\n")
        print(mem_reply)
        print("\n" + "=" * 60 + "\n")