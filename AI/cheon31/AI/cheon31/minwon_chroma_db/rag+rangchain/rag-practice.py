# 민원 db 에서 minwon 부분과, 답변을 chroma db 에 올라마 기반 사용 하지 않고 임베딩 모델 사용하여 해당 값들을 chroma db 에 메타데이터 형식으로 저장
# 답변 속도 자체는 빠를 예정, chroma 내부 기능으로 비슷한 답변의 결과를 출력 하는 요소가 있으며, 별도의 사용자 관리가 필요 없음.(할수도 없다)
#API 방식을 통해서 입출력 가능 .
from langchain_chroma import Chroma
from langchain.schema import Document
import pandas as pd
import mysql.connector
from langchain_huggingface import HuggingFaceEmbeddings
import shutil
import os

# 💾 MySQL에서 민원 데이터 가져오기
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="minwon"
)

query = "SELECT minwon, response FROM history"

df = pd.read_sql(query, conn)
print("✅ MySQL에서 불러온 데이터:", df.shape)
print("총 로드된 민원 수:", len(df))

# 🧠 임베딩 모델 로딩
embedding_model = HuggingFaceEmbeddings(
    model_name="snunlp/KR-SBERT-V40K-klueNLI-augSTS"
)

# 🧹 이전 Chroma DB 있으면 삭제 (필요 시)
if os.path.exists("./chroma_db"):
    shutil.rmtree("./chroma_db")

# 구성(chroma db 에 비관계형 데이터 삽입)-> 별도 항목 삭제 불가능. 따라서 통째로 삭제 및 지우도록 하고 , 일주일에 한번씩 mysql 에서 chroma 생성 해야한다
docs = []
for _, row in df.iterrows():
    minwon = row["minwon"]
    response = row["response"]

    doc = Document(
        page_content=minwon,
        metadata={
            "response": response,
            "source": "공무원수정본",
            "category": row.get("category", "기타")
        }
    )
    docs.append(doc)

# 🧠 Chroma DB 생성 및 저장
db = Chroma.from_documents(docs, embedding_model, persist_directory="./chroma_db") # 임베딩 모델 사용하여 db 에 저장
#db.persist()# 실제 저장
print("✅ Chroma DB에 임베딩 완료!")

# ✅ 저장된 Chroma DB 다시 불러오기( 디버깅 용)
db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)

# 🎯 유저 입력 기반 유사 민원 검색
while True:
    query = input("\n💬 민원 내용을 입력하세요 (exit 입력 시 종료): ").strip()

    if query.lower() == "exit":
        print("🛑 종료합니다!")
        break

    docs = db.similarity_search(query, k=2)

    if not docs:
        print("❌ 유사한 민원을 찾을 수 없습니다.")
    else:
        print(f"\n🔍 '{query}' 와 유사한 민원 {len(docs)}건 찾았습니다:")
        for i, doc in enumerate(docs):
            print(f"\n📄 유사 문서 {i + 1}")
            print("📝 민원 내용:", doc.page_content)
            print("💬 공무원 답변:", doc.metadata.get('response', '없음'))
            print("🏷 카테고리:", doc.metadata.get('category', '없음'))
            print("-" * 50)