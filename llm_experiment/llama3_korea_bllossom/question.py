
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def doanswer(question):

    model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B'

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    model.eval()

    PROMPT = '''[질문]에 대답하시오. 거짓을 말하면 안됩니다.'''


    instruction = f"""
    [질문]
    {question}

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

    print(tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True))
    
print("질문 입력:")
question = input()
doanswer(question)