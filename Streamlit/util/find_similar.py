from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import pandas as pd
from sqlalchemy import create_engine
import os
import shutil
from sentence_transformers import util
import util.state as state_util    # util.state 는 state_util 로
import streamlit   as st           # st 는 streamlit 으로
import traceback
from util.database import *

### 참고 내용####
#  reply = find_similar_respond(minwon_summary, answer_yogi, k)
# 해당 함수 사용하면 유사도 가져와서 적절한 답변 출력 합니다
# 념겨줘야 할 인자값 : 다른곳에서 생성된 (민원에대한요지)(공무원이작성한답변 요지)(k=1)로 지정
# MY sql db 에 answer_yogi  TEXT 형삭으로 속성 필요 합니다
# 해당 코드는 mysql 이 수정된후 자동으로 벡터 db 의 내용을 반영하지 않으므로 특정 주기에 따라
# MySQL에서 민원 데이터 가져와서 Chroma DB 만들어 줘야 합니다. 해당 과정에서 기존 Chroma DB  삭제후 다시 생성 됩니다. rebuild_chroma_db 메서드 호출하여 사용
#chroma 벡터 db 의 생성 위치는 os.path.exists("minwon_chroma_db/chroma_db"): 여기서 설정 가능 합니다.


# 혹여나   Document is not defined 해당 에러뜨면 from langchain_core.schema import Document 로 수정



EMBEDDING_MODEL_NAME = "nlpai-lab/KURE-v1"
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


# 1) MySQL에서 민원 데이터 가져와서 Chroma DB 만들기 ========================



# 해당 부분은 mysql --> chroma db 로 만드는 과정 ( 주기적으로 실행 필요)
def rebuild_chroma_db(
        #mysql_url: str = "mysql+pymysql://root:1234@localhost/minwon",
        #query= "SELECT answer_yogi, response FROM history",
        persist_directory= "minwon_chroma_db/chroma_db",
):

    # 1) 데이터 로드
    #engine = create_engine(mysql_url)
    df = run_query("SELECT answer_yogi, response FROM history") #pd.read_sql(query, engine)

    # 2) 기존 DB 폴더 삭제
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    # 4) Document 리스트 생성
    docs = []
    # 기존 for _, row in df.iterrows(): 블록 안에서
    for _, row in df.iterrows():
        raw = row.get("answer_yogi", "")
        # None 또는 NaN인 경우 빈 문자열로 대체
        text = raw if isinstance(raw, str) else str(raw or "")
        docs.append(Document(
            page_content=text.strip(),
            metadata={"response": row.get("response", "")}
        ))
    # 5) Chroma DB 생성 및 저장
    chroma_db = Chroma.from_documents(
        docs,
        embedding_model,
        persist_directory=persist_directory
    )
    return chroma_db

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

)

def ensure_chroma_db():
    persist_dir = "minwon_chroma_db/chroma_db"
    if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
        rebuild_chroma_db()


def llama_generate(prompt: str, max_tokens: int = 500) -> str:
    res = llm(prompt=prompt, max_tokens=max_tokens, stop=["<|eot_id|>"])
    return res["choices"][0]["text"]


# 3) 유사 민원 검색 + LLaMA 회신문 생성 함수 =================================
import traceback  # 꼭 맨 위에 import 되어 있어야 함

def RUNNING_RAG_CODE(minwon_summary: str, innput_answer_yogi: str, k: int = 1):
    ensure_chroma_db()

    try:
        db = Chroma(
            persist_directory="minwon_chroma_db/chroma_db",
            embedding_function=embedding_model
        )

        # 1) 유사 민원 검색
        results = db.similarity_search(innput_answer_yogi, k=k)
        docs_list = [doc.page_content for doc in results]

        query_emb = embedding_model.embed_query(innput_answer_yogi)
        doc_embs = embedding_model.embed_documents(docs_list)

        sims = util.cos_sim(query_emb, doc_embs)[0]

        for doc, sim_val in zip(results, sims):
            print(f'코사인 유사도: {sim_val:.4f}')

        cosine_threshold = 0.7
        similar_docs = [doc for doc, sim_val in zip(results, sims) if sim_val >= cosine_threshold]

        # 2) 유사 응답 정리
        vector_db_fixed_answer = ""
        for doc in similar_docs:
            vector_db_fixed_answer += f"\n{doc.metadata['response']}\n\n"

        print(f"DEBUG [현재 입력한 답변요지]: {innput_answer_yogi}")
        print(f"DEBUG [기존의 답변 내용]: {vector_db_fixed_answer}")

        # 3) 프롬프트 생성
        system_msg = """\
당신은 전문 공무원 AI 어시스턴트입니다.
민원 요지를 바탕으로 1번과 2번 항목을 정중하게 작성해주고,
3번은 [고정된 답변 내용]을 그대로 출력하세요.
4번은 [회신 양식을] 그대로 출력하세요.
단, 3.귀하의 민원사항에 대해~ 는 항상 그대로 시작해야 하며,
그 아래는 수정하지 말고 그대로 이어붙이세요.
"""

        if vector_db_fixed_answer.strip():
            user_msg = f"""\
[민원의 핵심 요점]
{minwon_summary}

[유사한 과거 답변 예시]
{vector_db_fixed_answer}

[아래 형식에 맞춰 새로운 회신을 작성하세요. 단, 3번항목만 그대로 붙여 쓰세요.]

[회신양식]
1.안녕하십니까? 귀하께서 국민신문고를 통해 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.
2.귀하께서 제출하신 민원의 내용은 [{minwon_summary}]에 관한 것으로 이해 (또는 판단) 됩니다.
3.귀하의 민원에 대한 검토 결과는 다음과 같습니다.
가.
나.
4. 답변 내용에 대한 추가 설명이 필요한 경우 {st.session_state.name} ({st.session_state.department} {st.session_state.tel})에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
감사합니다.

END
"""
            res = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=1028,
                stop=["END"],
            )
            mem_reply = res["choices"][0]["message"]["content"].strip()
        else:
            print("유사 답변 없음")
            mem_reply = "유사 답변 없음"

    except Exception as e:
        print("❗ [ERROR] RAG 응답 생성 중 예외 발생:")
        print("❗ minwon_chroma_db 폴더 삭제후 다시 STREAMLIT 실행 하세요 ")
        traceback.print_exc()
        mem_reply = ("===================================================\n"
                     "⚠️Chroma db 생성 및 데이터 참고에 실패하였습니다.\n "
                     "보통 Streamlit 내부의 minwon_chroma_db 폴더가 있을시 발생합니다. \n"
                     "혹은 MYSQL 의 DB 내용이 전혀 없을 경우 에러 발생합니다.\n"
                     "한 행 이상의 데이터를 추가해주세요\n"
                     "해당 폴더를 전체 삭제후 streamlit run 실행해주세요.\n "
                    
                     "현재 에러발생시 폴더 다시 삭제후 생성하는 로직은 미포함이며, 실 사용시"
                     "추가할 예정입니다. \n"
                     "==================================================\n")


    return mem_reply




# find_similar_respond -> respond함수 호출 (실제 스트림릿 사용시 해당 함수 호출 해서 사용 하면 됩니다) 굳이 사용안해도 될듯 합니다.

def find_similar_respond(minwon_summary: str | None = None,
                         answer_yogi: str | None = None,
                         k: int = 1) -> str:
    # 기본값이 없으면 세션에서 꺼내고
    if minwon_summary is None:
        minwon_summary = st.session_state.minwon_sub
    if answer_yogi is None:
        answer_yogi = st.session_state.answer_sub


    return RUNNING_RAG_CODE(minwon_summary, answer_yogi, k)

