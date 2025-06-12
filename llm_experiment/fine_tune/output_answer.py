import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json

answer1 ="""1. 귀하의 가정에 건강과 행복이 함께 하시길 기원합니다.
2. 귀하께서 신청하신 민원에 대하여 다음과 같이 답변 드립니다.
가. 민원요지
○ 사하구청소년문화의집 내 고우니홀 조명시설 확충 제안
나. 답변요지
○ 먼저, 사하구청소년문화의집 행사에 참여해 주시고 청소년 복지를 위한 발전방안을 제시해 주셔서 감사드립니다.
귀하께서 요청하신 사하구청소년문화의집 내 고우니홀 조명시설 확충은 계획수립, 예산확보 등 검토가 필요한 사안임을 알려드리며, 차후 제안내용이 추진될 수 있도록 부서에서 적극 검토·노력하도록 하겠습니다.
3. 답변내용에 대한 추가 설명이 필요한 경우 사하구 가족행복과(☎ 220-5631)로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다."""

answer2="""1. 다대도서관 운영에 많은 관심을 가져주셔서 감사드리며 귀하께서 요청하신 내용에 대하여 다음과 같이 답변드립니다.

2. 귀하의 민원내용은 “냉방으로 인한 불편”에 관한 것으로 이해됩니다.

3. 귀하의 요청사항에 대해 검토한 의견은 다음과 같습니다.
가. 열람실 내 에어컨 바람 방향을 회전으로 변경하여 공기 순환이 되게 조치하였습니다.
나. 환절기인 만큼 기온을 고려하여 온도조절에 신경쓰도록 하겠습니다.

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 추가로 더 궁금하신 사항이 있으시면 다대도서관 이하영 주무관(051-220-5865)에게 연락해 주시면 친절히 안내해 드리겠습니다. 감사합니다."""

model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B'

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

model.eval()

def aianswer(answer):
    PROMPT = '''당신은 민원 처리 결과에 대한 [답변]을 읽고, 해당 민원에 대해 담당자가 **무엇을 어떻게 조치했는지** 요약하는 요지 요약 봇입니다.

    다음의 [답변]을 읽고, 아래 조건에 따라 답변 요지를 간결하게 작성하세요.

    [요약 지침]
    - 구체적인 **조치 내용**과 **실행 방식**을 요약합니다.
    - 모호한 표현 대신 **실제로 한 일**을 명확히 기술합니다.
    - 형식: “무엇을 어떻게 조치하겠음 ,무엇을 어떻게 조치할 것임” 형태로 서술
    - 불필요한 인사말, 감정 표현, 반복 내용은 제외

    [예시1]
    [답변]
    해당 지역 도로 포장 불량 건에 대해 현장 확인을 완료하였으며, 관련 부서에 통보하여 보수작업을 진행하였습니다.
    [답변 요지]
    현장 확인 후 관련 부서에 보수작업 요청하겠음

    [예시2]
    [답변]
    제기된 쓰레기 무단 투기에 대해 구청 담당자가 현장 확인 후 해당 지역에 CCTV를 추가 설치하였습니다.
    [답변 요지]
    현장 확인 후 CCTV 추가 설치하겠음

    [예시3]
    [답변]
    1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.
    2. 귀하의 민원 내용은 「부산 당리승학 지역주택조합 공동주택 신축공사에서 발생하는 소음 및 분진으로 인한 생활불편」에 관한 것으로 이해됩니다.
    3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
    - 귀하의 불편사항을 현장관계자에게 전달하여 작업시간 준수, 고소음 작업 시 장비분산 사용, 작업자 교육 실시, 공사장 살수 철저 등 공사장 소음, 분진 최소화 할 수 있는 방안 마련하여 공사장 관리 철저토록 행정지도 하였습니다.
    - 추후에도 지속적으로 소음피해 발생 시 생활소음규제기준 준수 여부 확인을 위해 귀 댁에서 측정을 요청할 수 있으며, 해당 지역에 대한 지속적인 순찰을 통해 주민불편 사항이 최소화되도록 노력하겠습니다.
    4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 환경위생과 환경지도계(☎051-220-4397)으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다.
    [답변요지]
    현장관계자에게 전달, 작업시간 준수, 고소음 작업 시 장비분산 사용, 작업자 교육 등 공사장 관리 철저토록 행정지도,해당 지역 지속적인 순찰을 통해 주민 불편 사항 최소화'''


    instruction = f"""다음은 민원에 [답변]입니다.

    [답변]
    {answer}

    [답변요지]:"""

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

    return tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)


input_file = 'QAdata2.jsonl'
output_file = 'goodQAdata.jsonl'

line_count = 0

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
            answer = data.get('output', '')
            ai_result = aianswer(answer)
            data['answer'] = ai_result
            outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

            line_count += 1
            print(f"{line_count}줄 처리 완료")
            
        except json.JSONDecodeError as e:
            print(f"JSON 오류 발생: {e}")
        except Exception as e:
            print(f"기타 오류 발생: {e}")

# … 위에 aianswer() 함수 정의 등 …

def main():
    input_file  = 'QAdata2.jsonl'
    output_file = 'QAdata2_summaries.jsonl'
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        line_count = 0
        for line in infile:
            # … 기존 줄 단위 처리 로직 …
            line_count += 1
            print(f"{line_count}줄 처리 완료")

if __name__ == "__main__":
    main()
