from mteb import MTEB
from sentence_transformers import SentenceTransformer

# 1) 사용할 임베딩 모델 로드 (재혁이 모델!)
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

# 2) 평가할 태스크 리스트 지정
evaluation = MTEB(tasks=["STSBenchmark"])
#evaluation = MTEB(tasks=["KorSTS"])

# 3) 평가 실행
results = evaluation.run(
    model,
    output_folder="results/snunlp-KR-SBERT"
)