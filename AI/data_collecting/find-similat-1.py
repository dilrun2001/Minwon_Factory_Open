# util/find_similar.py

import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import pandas as pd
from sqlalchemy import create_engine
import os
import shutil
from sentence_transformers import util
import util.state as st  # Streamlit 세션 상태 가져오기

print("디버그: util/find_similar.py 모듈 로드됨")

### 참고 내용####
#   reply = find_similar_respond(minwon_summary, answer_yogi, k)
#   넘겨줘야 할 인자값 : (민원요지, 답변요지, k)
#   MySQL DB 에 answer_yogi TEXT, response TEXT 컬럼 필요
#   벡터 DB 위치: "minwon_chroma_db/chroma_db"

# 1) 임베딩 모델 정의
EMBEDDING_MODEL_NAME = "nlpai-lab/KURE-v1"
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# 2) Chroma 클라이언트용 Settings (New Clients API)
client_settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="minwon_chroma_db/chroma_db",
)

def get_chroma_client() -> chromadb.api.client.Client:
    """항상 이 함수로만 Chroma 클라이언트를 생성합니다."""
    print(f"디버그: get_chroma_client() 호출됨, 저장경로={client_settings.persist_directory}")
    return chromadb.Client(settings=client_settings)

def ensure_chroma_db():
    """DB 폴더가 없거나 비어 있으면 MySQL 로부터 재생성합니다."""
    print(f"디버그: ensure_chroma_db() 호출됨, 경로 확인 중: {client_settings.persist_directory}")
    d = client_settings.persist_directory
    if not os.path.exists(d) or not os.listdir(d):
        rebuild_chroma_db()

def rebuild_chroma_db(
    mysql_url: str = "mysql+pymysql://root:1234@localhost/minwon",
    query:     str = "SELECT answer_yogi, response FROM history",
):
    """MySQL에서 민원 데이터를 가져와 Chroma 벡터 DB를 새로 만듭니다."""
    print(f"디버그: rebuild_chroma_db() 호출됨, mysql_url={mysql_url}, query={query}")
    engine = create_engine(mysql_url)
    df = pd.read_sql(query, engine)
    print(f"디버그: rebuild_chroma_db() MySQL에서 {len(df)}행 로드됨")

    d = client_settings.persist_directory
    print(f"디버그: rebuild_chroma_db() 기존 디렉토리 삭제 시도: {d}")
    if os.path.exists(d):
        try:
            shutil.rmtree(d)
            print("디버그: 폴더 삭제 완료")
        except Exception as e:
            print(f"디버그: 폴더 삭제 중 오류 발생 – {e}")
    else:
        print("디버그: 폴더가 없어 삭제 안함")

    # 1) Chroma 클라이언트 생성 및 Collection 확보
    client = get_chroma_client()
    coll = client.get_or_create_collection(
        name="minwon_collection",
        embedding_function=embedding_model.embed_query  # 쿼리 → 벡터 함수 지정
    )

    # 2) MySQL 데이터 문서로 추가
    docs = []
    metadatas = []
    ids = []
    for i, row in df.iterrows():
        raw  = (row.get("answer_yogi") or "").strip()
        resp = row.get("response") or ""
        if not raw:
            continue
        docs.append(raw)
        metadatas.append({"response": resp})
        ids.append(str(i))
    print(f"디버그: rebuild_chroma_db() 인덱싱할 문서 {len(docs)}개 준비됨")

    if docs:
        coll.add(
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )
        print("디버그: rebuild_chroma_db() 문서 추가 완료")

    return client

# 3) LLaMA 모델 로딩 ===============================================
model_path = hf_hub_download(
    repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
    filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
)
llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    temperature=0.6,
    top_p=0.9,
    gpu_layers=-1,  # 모든 레이어를 GPU에서 실행
)

def RUNNING_RAG_CODE(minwon_summary: str, innput_answer_yogi: str, k: int = 1) -> str:
    print(f"디버그: RUNNING_RAG_CODE() 시작 → minwon_summary={minwon_summary}, answer_yogi={innput_answer_yogi}, k={k}")
    ensure_chroma_db()
    print("디버그: RUNNING_RAG_CODE() ensure_chroma_db 완료")

    client = get_chroma_client()
    coll = client.get_collection("minwon_collection")
    print("디버그: RUNNING_RAG_CODE() Chroma 클라이언트 및 Collection 획득 완료")

    print(f"디버그: RUNNING_RAG_CODE() query 실행 (k={k})")
    query_res = coll.query(
        query_texts=[innput_answer_yogi],
        n_results=k
    )

    docs      = query_res["documents"][0]
    metas     = query_res["metadatas"][0]
    distances = query_res["distances"][0]
    print(f"디버그: RUNNING_RAG_CODE() 쿼리 결과 문서 수={len(docs)}, 거리 값={distances}")

    # 거리가 작을수록 유사 → 임계값 예시 0.3 이하만 사용
    threshold = 0.3
    example_block = ""
    for doc_text, dist, meta in zip(docs, distances, metas):
        if dist <= threshold:
            example_block += f"\n{meta['response']}\n\n"
    print(f"디버그: RUNNING_RAG_CODE() example_block:\n{example_block}")

    system_msg = """\
당신은 전문 공무원 AI 어시스턴트입니다.
기존의 답변 내용에 맞추어 민원의 핵심 요점 부분만 수정해서 출력 해주세요.
끝맺음은 '~하였습니다.' 또는 '~되었습니다.' 로."""
    if example_block:
        user_msg = f"""\
[민원의 핵심 요점]
{minwon_summary}

[기존의 답변 내용]
{example_block}

END
"""
        print("디버그: RUNNING_RAG_CODE() LLaMA에 요청 전송")
        print("디버그: system_msg =", system_msg)
        print("디버그: user_msg =", user_msg)
        res = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=300,
            stop=["END"],
        )
        mem_reply = res["choices"][0]["message"]["content"].strip()
        print(f"디버그: RUNNING_RAG_CODE() LLaMA 응답: {mem_reply}")
        return mem_reply
    else:
        print("디버그: RUNNING_RAG_CODE() example_block 없음, 기본 메시지 반환")
        return "유사 답변 없음"

def find_similar_respond(
    minwon_summary: str | None = None,
    answer_yogi:    str | None = None,
    k: int = 1,
) -> str:
    if minwon_summary is None:
        minwon_summary = st.session_state.minwon_sub
    if answer_yogi is None:
        answer_yogi = st.session_state.answer_sub
    return RUNNING_RAG_CODE(minwon_summary, answer_yogi, k)
