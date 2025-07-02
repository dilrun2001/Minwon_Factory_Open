import json
import matplotlib.pyplot as plt
from bert_score import score

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

# 파일 경로
file_finetuned = "compare_q8_vs_finetuned.jsonl"
file_llama3 = "101-105Fight.jsonl"

# 점수 저장용 리스트
scores_finetuned = []
scores_q8 = []
scores_llama3 = []

# BERTScore 계산 함수
def compute_bertscore(candidates, references):
    _, _, F1 = score(candidates, references, lang='ko')
    return F1[0].item()

# 1. compare_q8_vs_finetuned.jsonl 처리
with open(file_finetuned, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        gt = data['ground_truth']
        finetuned = data['answer_finetuned']
        q8 = data['answer_q8']

        scores_finetuned.append(compute_bertscore([finetuned], [gt]))
        scores_q8.append(compute_bertscore([q8], [gt]))

# 2. 101-105Fight.jsonl 처리
with open(file_llama3, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        gt = data['ground_truth']
        llama3_answer = data['answer1']

        scores_llama3.append(compute_bertscore([llama3_answer], [gt]))

# 🔥 3. 결과 저장 (JSONL)
with open("bertscore.jsonl", "w", encoding="utf-8") as f:
    for i in range(len(scores_finetuned)):
        item = {
            "index": i,
            "finetuned": scores_finetuned[i],
            "q8": scores_q8[i],
            "llama3": scores_llama3[i]
        }
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# 4. 박스플롯 출력
plt.figure(figsize=(8, 6))
plt.boxplot([scores_finetuned, scores_q8, scores_llama3],
            labels=["Fine-tuned", "Q8 양자화", "LLaMA3 원본"])
plt.title("BERTScore 비교 (Fine-tuned vs Q8 vs LLaMA3)")
plt.ylabel("BERTScore (F1)")
plt.grid(axis='y')
plt.tight_layout()
plt.show()
