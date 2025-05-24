
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

minwon ="""당리동 포스코 공사 현장 소음 및 먼지
당리동 포스코 공사 현장 소음과 먼지로 인해 고통 받고 있습니다.
어제 오늘 먼지가 눈에 보이고 영상에 보일 정도로 심하게 나고 있는데
살수를 한다고 하는데 먼지가 이렇게 많이 날릴 수가 있습니까?
어제 포스코측 관리자와 연락을 하여 조치 하겠다고 하였는데
오늘도 같은곳에 먼지가 날리고 있습니다."""
answer ="""1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.
2. 귀하의 민원 내용은 「부산 당리승학 지역주택조합 공동주택 신축공사에서 발생하는 소음 및 분진으로 인한 생활불편」에 관한 것으로 이해됩니다.
3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
- 귀하의 불편사항을 현장관계자에게 전달하여 작업시간 준수, 고소음 작업 시 장비분산 사용, 작업자 교육 실시, 공사장 살수 철저 등 공사장 소음, 분진 최소화 할 수 있는 방안 마련하여 공사장 관리 철저토록 행정지도 하였습니다.
- 추후에도 지속적으로 소음피해 발생 시 생활소음규제기준 준수 여부 확인을 위해 귀 댁에서 측정을 요청할 수 있으며, 해당 지역에 대한 지속적인 순찰을 통해 주민불편 사항이 최소화되도록 노력하겠습니다.
4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 환경위생과 환경지도계(051-220-4397)으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다."""
answer_format="""1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.

2. 귀하의 민원 내용은 [민원요지]에 관한 것으로 이해됩니다.

3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
가. [답변요지]

4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 [부서명]([이름], [전화번호])으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다. """


model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B'

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

model.eval()

PROMPT = '''당신은 민원에 [답변]한 내용을 보고 민원을 어떻게 처리했는지에 대한 [답변요지]를 알려주는 봇입니다.'''
instruction = f"""다음은 민원에 [답변]입니다.

[답변]
{answer}"""

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
    pad_token_id=tokenizer.pad_token_id,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9
)

print(tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True))
