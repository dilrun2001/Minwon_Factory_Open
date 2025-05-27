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
        mysql_url: str = "mysql+pymysql://root:1234@localhost/minwon",
        query= "SELECT answer_yogi, response FROM history",
        persist_directory= "minwon_chroma_db/chroma_db",
):
    # 1) 데이터 로드
    engine = create_engine(mysql_url)
    df = pd.read_sql(query, engine)

    # 2) 기존 DB 폴더 삭제
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    # 4) Document 리스트 생성
    docs = []
    for _, row in df.iterrows():
        docs.append(Document(
            page_content=row["answer_yogi"].strip(),
            metadata={"response": row["response"]}
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


def llama_generate(prompt: str, max_tokens: int = 500) -> str:
    res = llm(prompt=prompt, max_tokens=max_tokens, stop=["<|eot_id|>"])
    return res["choices"][0]["text"]


# 3) 유사 민원 검색 + LLaMA 회신문 생성 함수 =================================
def RUNNING_RAG_CODE(minwon_summary: str, innput_answer_yogi: str, k: int = 1):


   #백터 db 에 저장 된거 가져옵니다.

    db = Chroma(persist_directory="minwon_chroma_db/chroma_db",embedding_function=embedding_model)



    # 1) 유사 민원 검색 (score 포함) 및 필터링
    results = db.similarity_search(innput_answer_yogi, k=k)
    docs_list = [doc.page_content for doc in results]

    query_emb = embedding_model.embed_query(innput_answer_yogi)
    doc_embs = embedding_model.embed_documents(docs_list)

    sims = util.cos_sim(query_emb, doc_embs)[0]

    for doc, sim_val in zip(results, sims):
        print(f'코사인 유사도: {sim_val:.4f}')

    cosine_threshold = 0.7
    similar_docs = [doc for doc, sim_val in zip(results, sims) if sim_val >= cosine_threshold]


    # 2) 프롬프트에 예시로 추가 어떤 것을 [답변 요지를 example_block 에 넣는다].
    vector_db_fixed_answer = ""
    for doc in similar_docs:
        vector_db_fixed_answer += f"""
    {doc.metadata["response"]}


"""
    # DEBUG: show injected prompt values
    #print(f"DEBUG [민원의 핵심 요점]: {minwon_summary}")  
    print(f"DEBUG [현재 입력한 답변요지]: {innput_answer_yogi}")
    print(f"DEBUG [기존의 답변 내용]: {vector_db_fixed_answer}")

    # 3) 본 프롬프트 구성 벡터 db 참고해서 답변을 생성한다. 참고 할게 없으면 답변 미출력.
    system_msg = """\
당신은 전문 공무원 AI 어시스턴트입니다.
기존의 답변 내용에 맞추어 민원의 핵심 요점 부분만 수정해서 출력 해주세요
탬플릿 부분의 문장 끝에는 반드시 '~하였습니다.' 또는 '~되었습니다.' 형태의 종결어미를 사용해야 합니다.
[기존의 답변 내용] 이후 부분만 출력해주세요.
"""
    if vector_db_fixed_answer.strip():
        # build user message with END sentinel
        user_msg = f"""\
[민원의 핵심 요점]
{minwon_summary}

[기존의 답변 내용]
{vector_db_fixed_answer}

[탬플릿]
1.안녕하십니까? 귀하께서 국민신문고를 통해 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.
2.귀하께서 제출하신 민원의 내용은 {minwon_summary} 에 관한 것으로 이해 (또는 판단) 됩니다.
3.귀하의 민원에 대한 검토 결과는 다음과 같습니다.
가.
나.
4. 답변 내용에 대한 추가 설명이 필요한 경우 000부 000과 홍길동 사무관 (010-101-101) 에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
감사합니다.



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




# find_similar_respond -> respond함수 호출 (실제 스트림릿 사용시 해당 함수 호출 해서 사용 하면 됩니다) 굳이 사용안해도 될듯 합니다.

def find_similar_respond(minwon_summary: str, answer_yogi: str, k=1):
    """
    minwon_summary: 외부에서 생성된 민원 요지
    answer_yogi: 사용자 입력 답변 요지
    """
    return RUNNING_RAG_CODE(minwon_summary, answer_yogi, k)















# # 4) 인터랙티브 실행 예시 ================================================
# if __name__ == "__main__":
#     # 한 번만 실행: 다중행 민원 내용 입력
#     print("💬 민원 내용을 입력하세요. 입력을 마치려면 빈 줄에서 엔터를 누르세요:")
#     minwon_lines = []
#     while True:
#         line = input()
#         if line == "":
#             break
#         minwon_lines.append(line)
#     minwon_text = "\n".join(minwon_lines).strip()
#     if minwon_text.lower() == "exit":
#         print("🛑 종료합니다!")
#         exit()
#
#     # 단일 행 답변 요지 입력
#     innput_answer_yogi = input("💬 답변 요지를 입력하세요: ").strip()
#     print('출력 중입니다. 기다려 주세요.')
#     mem_reply = respond_with_memory(
#         minwon_text=minwon_text,
#         innput_answer_yogi=innput_answer_yogi,
#         k=1
#     )
#
#     print("\n✨ [Chroma 참조 회신문]:\n")
#     print(mem_reply)
# # 프로그램 끝



