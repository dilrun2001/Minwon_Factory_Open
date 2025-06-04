
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

minwon ="""당리동 포스코 공사 현장 소음 및 먼지
당리동 포스코 공사 현장 소음과 먼지로 인해 고통 받고 있습니다.
어제 오늘 먼지가 눈에 보이고 영상에 보일 정도로 심하게 나고 있는데
살수를 한다고 하는데 먼지가 이렇게 많이 날릴 수가 있습니까?
어제 포스코측 관리자와 연락을 하여 조치 하겠다고 하였는데
오늘도 같은곳에 먼지가 날리고 있습니다."""
answer ="""현장관계자에게 전달, 작업시간 준수, 고소음 작업 시 장비분산 사용, 작업자 교육 등 공사장 관리 철저토록 행정지도,해당 지역 지속적인 순찰을 통해 주민 불편 사항 최소화"""
answer_format="""1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.

2. 귀하의 민원 내용은 [민원요지]에 관한 것으로 이해됩니다.

3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
가. [답변요지]

4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 [부서명]([이름], [전화번호])으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다. """


model_id = "./llama3-ko-minwon-finetuned"

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
