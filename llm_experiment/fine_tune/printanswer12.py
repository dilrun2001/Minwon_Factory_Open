import json

input_file = 'Fight.jsonl'

# 가져오고 싶은 줄 번호 (0-based index → 2=3번째 줄, 4=5번째 줄)
target_lines = [2, 4,11]

with open(input_file, 'r', encoding='utf-8') as infile:
    for i, line in enumerate(infile):
        if i in target_lines:
            try:
                data = json.loads(line.strip())
                print(f"\n✅ {i+1}번째 줄 출력:")
                print("[Ground Truth]")
                print(data.get('ground_truth', 'N/A'), '\n')
                print("[Answer 1]")
                print(data.get('answer1', 'N/A'), '\n')
                print("[Answer 2]")
                print(data.get('answer2', 'N/A'), '\n')
            except json.JSONDecodeError as e:
                print(f"JSON 오류 발생 (줄 {i+1}): {e}")