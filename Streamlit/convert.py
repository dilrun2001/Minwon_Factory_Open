import jsonlines

#pip install jsonlines

# jsonl 파일 읽어서 특정 target만 list에 저장
def jsonlload(fname, target):
    json_list = []
    with jsonlines.open(fname) as f:
        for line in f:
            json_list.append(line[target])
    return json_list


print(jsonlload('data.jsonl', "instruction"))