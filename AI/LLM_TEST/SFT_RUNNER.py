# 🧠 SFT 기반 민원 요약 및 조치 추론기
def run_sft_moin_reply(moin, model=None):
    """
    SFT 기반 민원 회신문 템플릿 프롬프트 생성기
    - moin: 민원 원문
    - model: 텍스트 생성 모델 함수 (없으면 prompt만 출력)
    """
    prompt = f"""다음 민원에 대해 회신문 템플릿의 빈칸에 들어갈 내용을 생성하세요.

민원 내용: {moin}

출력 형식:
요약: ...
조치1: ...
조치2: ...
"""
    return prompt if model is None else model(prompt)

# ✅ 테스트 예시
test1 = run_sft_moin_reply("다대포 해변 쓰레기가 너무 많고 악취가 심합니다. 조치 바랍니다.")
print(test1)