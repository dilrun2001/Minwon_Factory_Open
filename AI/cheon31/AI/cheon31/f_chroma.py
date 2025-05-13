import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os
import numpy as np

# 💡 0. 저장 경로 (폴더 없으면 만들기)
persist_path = "minwon_chroma_db"
os.makedirs(persist_path, exist_ok=True)

# 💡 1. Chroma 서버 구동 클라이언트
client = chromadb.PersistentClient(path=persist_path)  # ✅ 최신 방식은 여기서 경로 설정!

# 💡 2. 임베딩 함수 연결 (jhgan 한국어 SBERT)
embedding_fn = SentenceTransformerEmbeddingFunction(model_name="jhgan/ko-sbert-sts")

# 💡 3. 컬렉션 생성 또는 가져오기
collection = client.get_or_create_collection(
    name="minwon_rag_ko",
    embedding_function=embedding_fn
)

# 💡 4. 민원 데이터
yoji = "터널 입구 낙석 위험으로 인한 민원이 접수되었습니다"
original_answer = "확인 후 조치 예정입니다."
revised_answer = "시민의 안전 확보를 위해 낙석 방지 시설을 시급히 설치하겠습니다."

# 💡 5. 저장
collection.add(
    documents=[yoji],
    metadatas=[{
        "원래답변": original_answer,
        "수정답변": revised_answer,
        "카테고리": "도로안전"
    }],
    ids=["minwon001"]
)

print("✅ 최신 방식으로 ChromaDB에 저장 완료!")
print(f"📂 경로: {persist_path}")

# 💡 6. 저장된 전체 민원 데이터 출력
print("\n📋 [현재 저장된 민원 목록 보기]")
all_data = collection.get(include=["embeddings", "documents", "metadatas"])

for i in range(len(all_data["ids"])):
    print(f"🆔 ID: {all_data['ids'][i]}")
    print(f"📄 요지: {all_data['documents'][i]}")
    print(f"📌 임베딩 벡터: {all_data['embeddings'][i][:5]}...")  # 일부만 보기
    print(f"📝 수정답변: {all_data['metadatas'][i].get('수정답변', '없음')}")
    print("-" * 40)

# 💡 7. 사용자 입력 기반 유사 문장 검색
print("\n🔍 유사 민원 검색 테스트")
query_text = input("🔎 어떤 문장을 검색할까요? → ")

results = collection.query(
    query_texts=[query_text],
    n_results=1  # 가장 유사한 문장 1개만
)

# 💡 8. 유사도 점수 계산
# 쿼리 임베딩 구하기
query_embedding = embedding_fn([query_text])[0]  # 입력 문장을 임베딩
result_embedding = results['embeddings'][0][0]  # 가장 유사한 문장의 임베딩

# 코사인 유사도 계산
similarity = np.dot(query_embedding, result_embedding) / (
    np.linalg.norm(query_embedding) * np.linalg.norm(result_embedding)
)

print("\n🔍 [유사한 문장 검색 결과]")
print(f"📝 유사 문장: {results['documents'][0]}")
print(f"📌 ID: {results['ids'][0]}")
print(f"💬 수정답변: {results['metadatas'][0][0].get('수정답변', '없음')}")
print(f"📈 유사도 점수: {similarity:.4f}")
print("-" * 40)