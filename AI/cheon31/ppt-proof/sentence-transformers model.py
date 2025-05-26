from sentence_transformers import SentenceTransformer

# 모델 로드
model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')

# 임베딩할 문장들
sentences = ["빠른시일안에 처리 할수 있도록 하겠습니다", "현장 작업을 진행중입니다. 빠른시일안에 처리 할수 있도록 하겠습니다"]

# 문장 임베딩
embeddings = model.encode(sentences)

# 임베딩 결과 출력
for i, embedding in enumerate(embeddings):
    print(f"문장 {i+1} 임베딩 벡터:\n{embedding}\n")

