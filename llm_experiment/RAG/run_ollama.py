import ollama

print("AMD 9070 XT로 답변을 생성합니다...")

response = ollama.chat(model='llama3', messages=[
  {
    'role': 'user',
    'content': '파이썬으로 데이터 분석하는 코드 간단하게 짜줘. 한국어로 설명해줘.'
  },
])

print("\n[답변]")
print(response['message']['content'])