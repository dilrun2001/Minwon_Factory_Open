import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from sentence_transformers import SentenceTransformer, util

# ✅ KURE-v1 모델 로드 (유사도 비교용)
embedding_model = SentenceTransformer("nlpai-lab/KURE-v1")

answer_format = """1. 안녕하십니까? 귀하께서 신청하신 민원에 대한 검토결과를 다음과 같이 알려드립니다.

2. 귀하의 민원 내용은 [민원요지]에 관한 것으로 이해됩니다.

3. 귀하의 민원사항에 대해 검토한 결과는 다음과 같습니다.
가. [답변요지]

4. 귀하의 민원에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우 [부서명]([이름], [전화번호])으로 연락주시면 친절히 안내해 드리도록 하겠습니다. 감사합니다. """

def load_model(model_id):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    return tokenizer, model

def llama3vs(minwon, answer, tokenizer, model):
    PROMPT = '''당신은 공공기관의 민원 응답을 담당하는 전문 공무원입니다.
기관 이름은 '사하구청'입니다.

다음의 **[답변 템플릿] 형식을 정확히 지켜서** 작성하십시오. 
⚠️ [답변 템플릿]의 형식을 **그대로 유지하고**, 출력 시작 부분이나 끝에 어떠한 추가 설명도 하지 마십시오.

※ 반드시 출력은 [답변 템플릿] 안에 있는 형식을 따르며, 템플릿 외 문장은 추가하지 마십시오.
※ 템플릿 내 `[민원요지]` 부분은 민원 내용을 행정 문서 문체로 정중하게 요약하여 대체하되, `[민원요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
※ 템플릿 내 `[답변요지]` 부분은 답변 요지를 정중하고 행정적인 문체로 바꾸어 넣되, `[답변요지]`라는 단어는 최종 출력에 **표시되지 않아야 합니다**.
※ 출력에는 들여쓰기, 불필요한 줄바꿈, 공백 없이 문장 맨 앞에서 바로 시작하십시오.
※ 문장 끝에는 반드시 '~하였습니다.' 또는 '~되었습니다.' 형태의 종결어미를 사용해야 합니다.'''

    instruction = f"""다음은 민원에 대한 [답변 요지]와 [민원 내용]입니다.

[민원 내용]
{minwon}

[답변 요지]
{answer} 

[답변 템플릿]
{answer_format}"""

    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": instruction}
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

    return tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)

# ✅ 모델 로딩 (1회만 수행)
llama3_tokenizer, llama3_model = load_model("MLP-KTLim/llama-3-Korean-Bllossom-8B")
finetuned_tokenizer, finetuned_model = load_model("./llama3-ko-minwon-merged")

# ✅ 입력/출력 파일 설정
input_file = 'exampledata.jsonl'
output_file = 'Fight.jsonl'

line_count = 0

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
            minwon = data.get('instruction', '')
            output = data.get('output', '')
            answer = data.get('answer', '')

            # 생성된 두 답변
            answer1 = llama3vs(minwon, answer, llama3_tokenizer, llama3_model)
            answer2 = llama3vs(minwon, answer, finetuned_tokenizer, finetuned_model)

            # 임베딩 및 유사도 계산
            sentences = [output, answer1, answer2]
            embeddings = embedding_model.encode(sentences)
            sim1 = util.cos_sim(embeddings[0], embeddings[1]).item()
            sim2 = util.cos_sim(embeddings[0], embeddings[2]).item()

            # 출력
            print(f"\n✅ {line_count} 유사도 결과:")
            print(f"정답 vs 답변 1: {sim1:.4f}")
            print(f"정답 vs 답변 2: {sim2:.4f}")

            # 결과 저장
            result = {
                "instruction": minwon,
                "ground_truth": output,
                "answer1": answer1,
                "answer2": answer2,
                "sim1": sim1,
                "sim2": sim2
            }
            outfile.write(json.dumps(result, ensure_ascii=False) + '\n')
            line_count += 1
            print(f"{line_count}줄 처리 완료")

        except json.JSONDecodeError as e:
            print(f"JSON 오류 발생: {e}")
        except Exception as e:
            print(f"기타 오류 발생: {e}")
