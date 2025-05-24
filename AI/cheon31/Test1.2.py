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
engine = create_engine("mysql+pymysql://root:1234@localhost/minwon")
query = "SELECT answer_yogi,response FROM history"
df = pd.read_sql(query, engine)

if os.path.exists("minwon_chroma_db/chroma_db"):
    shutil.rmtree("minwon_chroma_db/chroma_db")

embedding_model = HuggingFaceEmbeddings(
    model_name="snunlp/KR-SBERT-V40K-klueNLI-augSTS"
)

docs = []
for _, row in df.iterrows():
    content = row["answer_yogi"].strip()
    docs.append(Document(page_content=content, metadata={"response": row["response"]}))

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
    gpu_layers=-1,
    verbose=False
)

def llama_generate(prompt: str, max_tokens: int = 500) -> str:
    res = llm(prompt=prompt, max_tokens=max_tokens, stop=["<|eot_id|>"])
    return res["choices"][0]["text"].strip()

# 3) 유사 민원 검색 + LLaMA 회신문 생성 함수 =================================
def respond_with_memory(minwon_text: str, innput_answer_yogi: str, k: int = 1):
    # 민원 요약
    minwon_summary = AI_print_minwon_sub(minwon_text).strip()

    # Chroma DB에서 유사 문서 검색
    db = Chroma(
        persist_directory="minwon_chroma_db/chroma_db",
        embedding_function=embedding_model
    )

    results = db.similarity_search_with_score(innput_answer_yogi, k=10)
    for doc, dist in results:
        print(f"DEBUG 유사도측정: {dist:.6f} → {doc.page_content[:40]}...")


    threshold = 160.0
    similar_docs = [doc for doc, dist in results if dist <= threshold]

    # 디버그 출력
    print(f"DEBUG [민원의 핵심 요점]: {minwon_summary}")
    print(f"DEBUG [현재 입력한 답변요지]: {innput_answer_yogi}")
    if similar_docs:
        vector_db_fixed_answer = "\n".join(d.metadata["response"] for d in similar_docs)
        print(f"DEBUG [기존의 답변 내용]:\n{vector_db_fixed_answer}")
    else:
        vector_db_fixed_answer = ""
        print("DEBUG [기존의 답변 내용]: (유사 답변 없음)")

    # 회신문 생성
    if vector_db_fixed_answer:
        system_msg = """\
        당신은 전문 공무원 AI 어시스턴트입니다.
        아래 **[답변 템플릿]** 형식을 **정확히** 지켜서, **추가 설명 없이** 템플릿 1~4번 항목만 출력하십시오.
        - “[민원의 핵심 요점]” 등 라벨은 절대 출력하지 않습니다.
        - 1·2·4번 항목은 고정 텍스트를 그대로 사용하되, 2번에는 실제 요약문을 삽입합니다.
        -3번 항목의 각 하위 문장은 입력값을 활용하여, 반드시 ‘~하였습니다.’ 또는 ‘~되었습니다.’ 형태의 높임말로 끝나야 합니다.
        -절대로 ‘[민원의 핵심 요점]’, ‘[현재 입력한 답변요지]’처럼 대괄호 라벨은 출력하지 마십시오.
        """

        user_msg = f"""\
        [민원의 핵심 요점]
        {minwon_summary}

        [기존의 답변 내용]
        {vector_db_fixed_answer}

        [답변 템플릿]
        1. 안녕하십니까? …  
        2. 귀하께서 제출하신 민원의 내용은 {minwon_summary}으로 이해 (또는 판단) 됩니다.  
        3. 귀하의 민원에 대한 검토 결과는 다음과 같습니다.  
        가. **아래 내용을 정중한 행정 문체로 다듬어 작성해 주십시오:**  
           “{innput_answer_yogi}”  
        4. …  
        END
        """

        res = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=300,
            stop=["END"],
        )
        return res["choices"][0]["message"]["content"].strip()
    else:
        return "유사 답변 없음"

# 4) 인터랙티브 실행 예시 ================================================
if __name__ == "__main__":
    print("💬 민원 내용을 입력하세요. (빈 줄에서 엔터→종료)")
    minwon_lines = []
    while True:
        line = input()
        if not line:
            break
        minwon_lines.append(line)
    minwon_text = "\n".join(minwon_lines).strip()
    if minwon_text.lower() == "exit":
        print("🛑 종료합니다!")
        exit()

    innput_answer_yogi = input("💬 답변 요지를 입력하세요: ").strip()
    print("출력 중입니다. 기다려 주세요.")
    mem_reply = respond_with_memory(minwon_text, innput_answer_yogi, k=1)

    print("\n✨ [Chroma 참조 회신문]:\n")
    print(mem_reply)