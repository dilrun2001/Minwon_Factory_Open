import matplotlib.pyplot as plt  # ← matplotlib.pyplot로 수정
import json

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

# 데이터 저장 리스트
sim1_values = []
sim2_values = []

input_file = 'Fight.jsonl'
line_count = 0

# ✅ JSONL 파일에서 sim1, sim2 수치 추출
with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
            sim1 = data.get('sim1', None)
            sim2 = data.get('sim2', None)

            if sim1 is not None and sim2 is not None:
                sim1_values.append(sim1)
                sim2_values.append(sim2)

            line_count += 1

        except json.JSONDecodeError as e:
            print(f"JSON 오류 발생: {e}")
        except Exception as e:
            print(f"기타 오류 발생: {e}")

print(f"\n총 {line_count}줄 처리 완료, 그래프 그리는 중...")

# ✅ 시각화
plt.figure(figsize=(12, 6))
plt.plot(sim1_values, label='LLaMA3 원본 모델', marker='o')
plt.plot(sim2_values, label='LLaMA3 파인튜닝 모델', marker='x')
plt.xlabel('샘플 번호')
plt.ylabel('유사도 점수')
plt.title('모델별 민원 응답 유사도 비교')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
