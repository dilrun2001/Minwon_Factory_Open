import matplotlib.pyplot as plt  # ← matplotlib.pyplot로 수정
import json
import numpy as np
from matplotlib.cbook import boxplot_stats

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

# 데이터 저장 리스트
sim1_values = []
sim2_values = []
sim3_values = []
time1_values =[]
time2_values =[]

llamaBest=0
finetuneBest =0
Q8Best=0

llamaWorst=1
finetuneWorst=1
Q8Worst=1

input_file = 'compare_q8_vs_finetuned.jsonl'
line_count = 0

# ✅ JSONL 파일에서 sim1, sim2 수치 추출
with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
            sim1 = data.get('sim_finetuned', None)
            sim2 = data.get('sim_q8', None)
            time1 = data.get('runtime_finetuned', None)
            time2 = data.get('runtime_q8', None)


            if sim1 is not None and sim2 is not None:
                sim1_values.append(sim1)
                sim2_values.append(sim2)
                if(finetuneBest < sim1):
                    finetuneBest =sim1
                    word1Best = data.get('answer_finetuned',None)
                if(finetuneWorst > sim1):
                    finetuneWorst = sim1
                    word1Worst = data.get('answer_finetuned',None)
                if(Q8Best < sim2):
                    Q8Best =sim2
                    word2Best = data.get('answer_q8',None)
                if(Q8Worst > sim2):
                    Q8Worst = sim2
                    word2Worst = data.get('answer_q8',None)


            if time1 is not None and time2 is not None:
                time1_values.append(time1)
                time2_values.append(time2)


            line_count += 1

        except json.JSONDecodeError as e:
            print(f"JSON 오류 발생: {e}")
        except Exception as e:
            print(f"기타 오류 발생: {e}")

print(f"\n총 {line_count}줄 처리 완료, 그래프 그리는 중...")

input_file = '101-105Fight.jsonl'

with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
            sim3 = data.get('sim1', None)

            if sim1 is not None and sim2 is not None:
                sim3_values.append(sim3)
                if(llamaBest < sim3):
                    llamaBest =sim3
                    word3Best = data.get('answer1',None)
                if(llamaWorst > sim3):
                    llamaWorst = sim3
                    word3Worst = data.get('answer1',None)                

            line_count += 1

        except json.JSONDecodeError as e:
            print(f"JSON 오류 발생: {e}")
        except Exception as e:
            print(f"기타 오류 발생: {e}")

print(f"\n총 {line_count}줄 처리 완료, 그래프 그리는 중...")

# ✅ 시각화
plt.figure(figsize=(12, 6))
plt.plot(sim1_values, label='LLaMA3 파인튜닝 모델', marker='o')
plt.plot(sim2_values, label='LLaMA3 Q8', marker='x')
plt.plot(sim3_values, label='원래모델', marker='x')
plt.xlabel('샘플 번호')
plt.ylabel('유사도 점수')
plt.title('모델별 민원 응답 유사도 비교')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


data = [sim1_values, sim2_values, sim3_values]
labels = ['LLaMA3 파인튜닝', 'Q8양자화', '원래 모델']

# 박스플롯 통계 추출
stats = boxplot_stats(data)

# 각 모델의 Q1, Q2, Q3 출력
for i, stat in enumerate(stats):
    print(f"[{labels[i]}]")
    print(f" - Q1 (25%): {stat['q1']}")
    print(f" - Q2 (Median): {stat['med']}")
    print(f" - Q3 (75%): {stat['q3']}")
    print(f" - Outliers: {stat['fliers']}")
    print()

# 박스플롯 그리기
plt.figure(figsize=(8, 6))
plt.boxplot(data, labels=labels)
plt.ylabel('유사도 점수')
plt.title('모델별 유사도 점수 분포 (Boxplot)')
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()


plt.figure(figsize=(12, 6))
plt.plot(time1_values, label='LLaMA3 파인튜닝 모델', marker='o')
plt.plot(time2_values, label='LLaMA3 Q8', marker='x')
plt.xlabel('샘플 번호')
plt.ylabel('시간(초)')
plt.title('모델별 답변시간')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

print(np.mean(time1_values))
print(np.mean(time2_values))

print(llamaBest)
print(llamaWorst)
print(finetuneBest)
print(finetuneWorst)
print(Q8Best)
print(Q8Worst)

print(word1Best)
print('\n\n\n')
print(word1Worst)
print('\n\n\n')
print(word2Best)
print('\n\n\n')
print(word2Worst)
print('\n\n\n')
print(word3Best)
print('\n\n\n')
print(word3Worst)