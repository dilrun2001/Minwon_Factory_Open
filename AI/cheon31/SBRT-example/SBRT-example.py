from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from sklearn.metrics.pairwise import cosine_similarity
# 해당 과정은 snunlp/KR-SBERT-V40K-klueNLI-augSTS 해당 모델을 사용하여 파인튜닝을 할수 있는 예제 입니다.

# 모델 로드
model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')

# 학습용 예제 구성
train_examples = [
    InputExample(texts=["그는 점심을 먹었다", "그는 식사를 했다"], label=1.0),
    InputExample(texts=["그는 점심을 먹었다", "그는 달렸다"], label=0.0)
]

# DataLoader 설정
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=4)

# 학습 손실 함수 설정
train_loss = losses.CosineSimilarityLoss(model)

# 모델 학습
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=10)



# 학습이 끝난 뒤, 문장 유사도 확인
sentences = ["그는 점심을 먹었다", "그는 식사를 했다", "그는 달렸다"]
embeddings = model.encode(sentences)

from sklearn.metrics.pairwise import cosine_similarity

# 문장 0 vs 1, 문장 0 vs 2 의 유사도 계산
sim_01 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
sim_02 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]

print(f"문장 0 vs 1 유사도: {sim_01:.4f}")
print(f"문장 0 vs 2 유사도: {sim_02:.4f}")


# 추가: 두 문장 유사도 비교
sent1 = "빠른시일안에 처리 할수 있도록 하겠습니다"
sent2 = "현장 작업을 진행중입니다. 빠른시일안에 처리 할수 있도록 하겠습니다"

# 두 문장 임베딩을 한 번에 계산
emb_pair = model.encode([sent1, sent2])

# sklearn의 cosine_similarity로 유사도 계산
sim_pair = cosine_similarity([emb_pair[0]], [emb_pair[1]])[0][0]
print(f"문장 sent1 vs sent2 유사도: {sim_pair:.4f}")