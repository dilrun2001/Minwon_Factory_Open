from util.find_similar import *

model = load_embedding_model()
df, embeddings =load_vector_data()
user_input = """구정업무에 수고가 많으십니다.
무궁화꽃나무 한그루 보호요청 드립니다.
다대1동 다대중학교위 송학탕에서 위로 약천사길 초입에 오래된 무궁화꽃 나무 한그루가 해마다 꽃을 피워 국화로서 위엄을 보여주고 있습니다.
그런데 어찌된 일인지 나무의 밑둥이 세멘트독으로 감싸져 있어 나무가 기형적으로 성장하고 있으니 현장 방문하시어 어떻게 조치하여 보호가
될수 있으면 좋겠습니다.
감사합니다."""
results = search_vector_data(user_input, df, embeddings, model, top_k=2)
    
best = results[0]
print(f"\n✅ 유사도: {best['score']:.4f}\n")
print(f"유사 민원:\n {best['minwon']}\n")
print(f"답변 내용:\n {best['response']}\n")

second = results[1]

print(f"\n✅ 유사도: {second['score']:.4f}\n")
print(f"유사 민원:\n {second['minwon']}\n")
print(f"답변 내용:\n {second['response']}\n")