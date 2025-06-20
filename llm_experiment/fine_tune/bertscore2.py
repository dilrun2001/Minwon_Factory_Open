import json
import numpy as np

# 점수 리스트 초기화
scores_finetuned = []
scores_q8 = []
scores_llama3 = []

# JSONL 파일 읽기
with open("bertscore.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        scores_finetuned.append(data["finetuned"])
        scores_q8.append(data["q8"])
        scores_llama3.append(data["llama3"])

# 통계 출력 함수
def print_stats(name, scores):
    scores_array = np.array(scores)
    print(f"▶ {name} 모델")
    print(f" - 중앙값 (Median): {np.median(scores_array):.4f}")
    print(f" - 최댓값 (Max): {np.max(scores_array):.4f}")
    print(f" - 상위 75% (Q3): {np.percentile(scores_array, 75):.4f}")
    print(f" - 하위 25% (Q1): {np.percentile(scores_array, 25):.4f}")
    print()

# 결과 출력
print_stats("Fine-tuned", scores_finetuned)
print_stats("Q8 양자화", scores_q8)
print_stats("LLaMA3 원본", scores_llama3)
