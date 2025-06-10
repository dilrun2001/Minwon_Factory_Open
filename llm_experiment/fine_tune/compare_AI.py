import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

minwon = """뉴스를 보면 사상구와 남구에서 곧 재난지원금이 지급되는걸로 보도되고 있습니다.
이번에 타구에서 구민들에게 지급되는 재난지원금이라는 부분이,
사하구에서는 이미 지급된 부분인지?, 아니면 사하구는 지급 예정이 없는 것인지?...궁금합니다.
그리고
보도에 따르면 난데없이 이번 사하구에서 종교시설에 시설당 100만원씩 지급한다는 기사를 본것 같습니다.
이게 사실일까요?
국민이나 더 좁게는 구민들 중에서는 종교인과 비종교인이 있고 나아가 무신론자가 있는데...
아이돌봄센터나 노인정 같은 사회복지 시설도 아니고
왜 종교 시설에 지우너을 해야 하는지 모르겠습니다.
전 국민이 모두 종교를 가지고 있다면 종교의 종류를 불문하고 지원할 수도 있겠지만...
유독 종교시설에
지원금을 세금으로 지급해야 하는지 납득하기 힘드네요.
정부에서 조차도 종교시설에만 특별히 별도의 지원금을 결정한 적은 없지 않나요?
부디 재고 하시고 그 비용을 보다 광범위한 지원에 사용하시면 좋을 것 같습니다."""

answer ="""사하구 재난지원금 지급여부 및 지급계획: 사상구 2차, 남구 3차 재난지원금 지급, 사하구 2차 재난지원금 선불카드 형태로 지급, 3차 지원금 계획 없음.
종교시설 재난방역지원금 지원: 종교시설 지원 대상 포함, 5월 중 방역물품 구입 지원."""

answer_format="""1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.

2. 귀하의 민원 내용은 [민원요지]에 관한 것으로 이해됩니다.

3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
가. [답변요지]

4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 [부서명]([이름], [전화번호])으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다. """

def llama3vs(minwon,answer):

    model_id = "MLP-KTLim/llama-3-Korean-Bllossom-8B"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    model.eval()

    PROMPT = '''당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
    기관 이름은 '사하구청'입니다.

    다음의 **[답변 템플릿] 형식을 정확히 지켜서** 작성하십시오. 
    ⚠️ [답변 템플릿]의 형식을 **그대로 유지하고**, 출력 시작 부분이나 끝에 어떠한 추가 설명도 하지 마십시오.

    ※ 반드시 출력은 [답변 템플릿] 안에 있는 형식을 따르며, 템플릿 외 문장은 추가하지 마십시오.
    ※ 템플릿 내 `[민원요지]` 부분은 민원 내용을 행정 문서 문체로 정중하게 요약하여 대체하되, `[민원요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
    ※ 템플릿 내 `[답변요지]` 부분은 답변 요지를 정중하고 행정적인 문체로 바꾸어 넣되, `[답변요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
    ※ 출력에는 들여쓰기, 불필요한 줄바꿈, 공백 없이 문장 맨 앞에서 바로 시작하십시오.'''
    instruction = f"""다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

    [민원 내용]
    {minwon}

    [답변 요지]
    {answer} 

    [답변 템플릿]
    {answer_format}"""

    messages = [
        {"role": "system", "content": f"{PROMPT}"},
        {"role": "user", "content": f"{instruction}"}
        ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = model.generate(
        input_ids,
        max_new_tokens=2048,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9
    )

    print(tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True))
    return tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)

def finetunedllamavs(minwon,answer):

    model_id = "./llama3-ko-minwon-merged"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    model.eval()

    PROMPT = '''당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
    기관 이름은 '사하구청'입니다.

    다음의 **[답변 템플릿] 형식을 정확히 지켜서** 작성하십시오. 
    ⚠️ [답변 템플릿]의 형식을 **그대로 유지하고**, 출력 시작 부분이나 끝에 어떠한 추가 설명도 하지 마십시오.

    ※ 반드시 출력은 [답변 템플릿] 안에 있는 형식을 따르며, 템플릿 외 문장은 추가하지 마십시오.
    ※ 템플릿 내 `[민원요지]` 부분은 민원 내용을 행정 문서 문체로 정중하게 요약하여 대체하되, `[민원요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
    ※ 템플릿 내 `[답변요지]` 부분은 답변 요지를 정중하고 행정적인 문체로 바꾸어 넣되, `[답변요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
    ※ 출력에는 들여쓰기, 불필요한 줄바꿈, 공백 없이 문장 맨 앞에서 바로 시작하십시오.'''
    instruction = f"""다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

    [민원 내용]
    {minwon}

    [답변 요지]
    {answer} 

    [답변 템플릿]
    {answer_format}"""

    messages = [
        {"role": "system", "content": f"{PROMPT}"},
        {"role": "user", "content": f"{instruction}"}
        ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = model.generate(
        input_ids,
        max_new_tokens=2048,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9
    )

    print(tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True))
    return tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)

a = llama3vs(minwon,answer)
b = finetunedllamavs(minwon,answer)

print(a)
print(b)