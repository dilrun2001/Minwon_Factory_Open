from mteb import MTEB
from sentence_transformers import SentenceTransformer

# 1) 모델 불러오기
model_name = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
model = SentenceTransformer(model_name)

# 2) 평가할 태스크 목록 지정
tasks = ["STSBenchmark"]  # 예: 문장 유사도 평가
evaluation = MTEB(tasks=tasks)

# 3) 벤치마크 실행 및 결과 저장
results = evaluation.run(
    model,
    output_folder=f"results/{model_name}"
)
print("✅ 벤치마크 완료! 결과는:", results)