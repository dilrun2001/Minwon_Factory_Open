
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


model_id = "./llama3-ko-munwon-finetuned"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

model.eval()

PROMPT = ''' 당신은 계산기 입니다 주어진 식을 계산하시오.'''
instruction = f"""9.9-9.11"""

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
