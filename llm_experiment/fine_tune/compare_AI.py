import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from output_answer import aianswer

# ──── 모델 & 토크나이저를 한 번만 로드 ────
MODEL1_ID = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
MODEL2_ID = "./llama3-ko-minwon-merged"

print("모델 로딩 중… (한 번만 실행됩니다)")
tokenizer1 = AutoTokenizer.from_pretrained(MODEL1_ID)
model1     = AutoModelForCausalLM.from_pretrained(
    MODEL1_ID,
    torch_dtype=torch.bfloat16,
    torch_device="cuda",
    load_in_8bit=True
)
model1.eval()

tokenizer2 = AutoTokenizer.from_pretrained(MODEL2_ID)
model2     = AutoModelForCausalLM.from_pretrained(
    MODEL2_ID,
    torch_dtype=torch.bfloat16,
    torch_device="cuda",
    load_in_8bit=True
)
model2.eval()
print("모델 로딩 완료!")

PROMPT = """당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
기관 이름은 '사하구청'입니다.

다음의 **[답변 템플릿] 형식을 정확히 지켜서** 작성하십시오. 
⚠️ [답변 템플릿]의 형식을 **그대로 유지하고**, 출력 시작 부분이나 끝에 어떠한 추가 설명도 하지 마십시오.

※ 출력에는 들여쓰기, 불필요한 줄바꿈, 공백 없이 문장 맨 앞에서 바로 시작하십시오.
"""
ANSWER_FORMAT = """1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.

2. 귀하의 민원 내용은 [민원요지]에 관한 것으로 이해됩니다.

3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
가. [답변요지]

4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 [부서명]([이름], [전화번호])으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다. """

def generate_reply(model, tokenizer, minwon, summary):
    instruction = f"""다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

[민원 내용]
{minwon}

[답변 요지]
{summary}

[답변 템플릿]
{ANSWER_FORMAT}"""
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user",   "content": instruction}
    ]
    # apply the chat template (this is library-specific)
    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    output_ids = model.generate(
        input_ids,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=False,
        num_beams=1
    )
    return tokenizer.decode(
        output_ids[0][input_ids.shape[-1]:],
        skip_special_tokens=True
    )

def main():
    input_file  = "QAdata2.jsonl"
    output_file = "compare_results.jsonl"

    # 결과 파일 초기화
    open(output_file, "w", encoding="utf-8").close()

    with open(input_file,  "r", encoding="utf-8") as fin, \
         open(output_file, "a", encoding="utf-8") as fout:

        for idx, line in enumerate(fin, start=1):
            data        = json.loads(line)
            minwon_raw  = data.get("instruction", "").strip()
            answer_raw  = data.get("output", "").strip()

            # 1) 민원 원답(output_answer)에서 요지 생성
            summary = aianswer(answer_raw)

            # 2) 두 모델에 모두 동일한 minwon+summary 입력
            out1 = generate_reply(model1, tokenizer1, minwon_raw, summary)
            out2 = generate_reply(model2, tokenizer2, minwon_raw, summary)

            # 3) JSONL로 결과 기록
            result = {
                "instruction": minwon_raw,
                "raw_answer":  answer_raw,
                "summary":     summary,
                "model1":      out1,
                "model2":      out2
            }
            fout.write(json.dumps(result, ensure_ascii=False) + "\n")
            print(f"{idx} 건 처리 완료")

if __name__ == "__main__":
    main()