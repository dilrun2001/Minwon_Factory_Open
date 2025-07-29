import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

minwon ="""안녕하세요. 저는 부산 사하구에 위치한 대학교에 재학 중인 학생입니다. 현재는 기숙사에서 생활하고 있으며 오는 12월부터 자취를 시작할 예정인데, 본가가 멀어 혼자 방을 알아봐야 하는 상황에 있습니다. 이와 관련하여 안심주거매니저 프로그램의 확대 운영을 건의하고자 합니다.

안심주거매니저는 아동복지시설에서 자립을 준비하는 청년들에게 큰 도움을 주는 정책입니다. 하지만 이 프로그램이 자립준비청년에 국한되지 않고, 모든 청년에게 확대될 수 있다면, 더욱 많은 청년들이 안정적으로 주거를 마련할 수 있을 것입니다. 현재 서울과 부산진구에서는 모든 청년에게 이와 유사한 서비스를 제공하고 있으며, 이는 청년들의 자립에 큰 기여를 하고 있습니다.

부산 사하구에서도 이러한 정책을 확대하여 다양한 청년들이 혜택을 받을 수 있도록 해주셨으면 합니다. 자취를 고민하는 많은 학생들과 청년들이 보다 안전하고 안정적인 주거 환경을 마련할 수 있도록 도와주시면 좋겠습니다.

부디 이 건의가 긍정적으로 검토되어, 사하구의 모든 청년들이 안심하고 주거를 마련할 수 있는 기회를 가질 수 있기를 바랍니다.

감사합니다."""

answer ="""주거안심매니저 사업 확대 운영 건의에 대해 홍보 중, 자립준비 청년들에게 정보 제공 및 시설 협력 요청함."""
answer_format="""1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.

2. 귀하의 민원 내용은 [민원요지]에 관한 것으로 이해됩니다.

3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
가. [답변요지]

4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 [부서명]([이름], [전화번호])으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다. """


model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B'

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=True,
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config,
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
instruction = f""""다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

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
    pad_token_id=tokenizer.pad_token_id,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9
)

print(tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True))