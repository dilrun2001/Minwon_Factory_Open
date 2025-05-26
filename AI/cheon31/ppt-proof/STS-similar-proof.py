from datasets import load_dataset
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'AppleGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# 1. KorSTS 로딩
ds = load_dataset("kor_nlu", "sts")["test"]

# 2. 모델 불러오기
model = SentenceTransformer("Alibaba-NLP/gte-Qwen2-7B-instruct")
#model = SentenceTransformer("nlpai-lab/KURE-v1")

# 3. 유사도 4.5 이상 문장쌍 추리기 sts 데이터 셋에서 사람이 4.5 이상인것들  즉 의미가 같은 데이터 들만 추출 하여
#이떄 해당 데이터들을 코사인 유사도를 계산하여
#히스토그램에 표시, 실제 실행해보면 0.8 이후로 비슷한 데이터가 많은것들을 파악 .

pairs = [(ex['sentence1'], ex['sentence2']) for ex in ds if ex['score'] >= 4.5]

# 4. 코사인 유사도 계산
scores = []
for s1, s2 in pairs:
    emb1 = model.encode(s1, convert_to_tensor=True)
    emb2 = model.encode(s2, convert_to_tensor=True)
    sim = util.cos_sim(emb1, emb2).item()
    scores.append(sim)

# 5. 시각화
plt.hist(scores, bins=30)
plt.xlabel("코사인 유사도 ")
plt.ylabel("항목별 갯수 ")
plt.title("코사인 유사도 분포도 (KorSTS Label ≥ 4.5)")
plt.axvline(x=0.8, color='red', linestyle='--', label="Threshold: 0.8")
plt.legend()
plt.show()