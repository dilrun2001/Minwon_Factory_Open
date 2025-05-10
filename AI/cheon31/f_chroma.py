#별도의 <임베딩 모델>을 사용해서 답변 요지에 맞는 tocken value 를 찾아서
#LLAMA 에서 prompt 를 제공하여 이전 답변을 기반으로 출력하기 .
# 사용자 민원을 -> chroma vector db 에 넣어 문장들을 토큰 형식으로 삽입

import chromadb
from sentence_transformers import SentenceTransformer
import uuid

# 1. Chroma DB 초기화 (최신 버전용)
client = chromadb.PersistentClient(path="./minwon_chroma_db")

# 2. 벡터 임베딩 모델 불러오기
embedding_model = SentenceTransformer("jhgan/ko-sbert-sts")

# 3. 컬렉션 생성 or 가져오기
collection = client.get_or_create_collection("minwon_edited")


# ✅ 사람이 수정한 답변 저장 함수
def save_edited_response(prompt: str, answer: str):
    vector = embedding_model.encode(prompt).tolist()
    uid = str(uuid.uuid4())  # ID는 중복 방지용으로 자동 생성
    collection.add(
        documents=[prompt],
        metadatas=[{"answer": answer}],
        ids=[uid],
        embeddings=[vector]
    )
    print(f"\n✅ 저장 완료!")
    print(f"프롬프트: {prompt}")
    print(f"수정 답변: {answer}")
    print(f"ID: {uid}")


# ✅ 유사한 프롬프트 찾아주는 함수
def find_similar_prompt(prompt: str, threshold: float = 0.85):
    vector = embedding_model.encode(prompt).tolist()
    result = collection.query(query_embeddings=[vector], n_results=1)

    if result['distances'][0][0] < (1 - threshold):
        return result['documents'][0][0], result['metadatas'][0][0]['answer']
    else:
        return None, None


# ✅ 테스트 흐름 실행
if __name__ == "__main__":
    print("🎯 Chroma 벡터 DB 테스트!")

    while True:
        print("\n무엇을 하시겠습니까?")
        print("1. 민원 프롬프트 + 수정답변 저장")
        print("2. 유사 민원 검색")
        print("3. 종료")
        choice = input("👉 선택 (1/2/3): ")

        if choice == "1":
            prompt = input("📝 민원 프롬프트 입력: ")
            answer = input("💬 사람이 수정한 답변 입력: ")
            save_edited_response(prompt, answer)

        elif choice == "2":
            search_prompt = input("🔍 검색할 민원 프롬프트 입력: ")
            match_prompt, match_answer = find_similar_prompt(search_prompt)

            if match_prompt:
                print("\n✅ 유사한 과거 민원 발견!")
                print(f"🔎 과거 프롬프트: {match_prompt}")
                print(f"💡 저장된 답변: {match_answer}")
            else:
                print("❌ 유사한 민원 없음. 새로 생성 필요!")

        elif choice == "3":
            print("👋 종료합니다!")
            break

        else:
            print("❗잘못된 입력입니다. 1/2/3 중에서 선택해주세요.")