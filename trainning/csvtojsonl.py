
# input_csv = "C:/Users/90608/Desktop/总集篇/Final.csv"
# output_jsonl = "C:/Users/90608/Desktop/总集篇/Final.jsonl"


import csv
import json

input_csv = "C:/Users/90608/Desktop/总集篇/Final.csv"
output_jsonl = "C:/Users/90608/Desktop/总集篇/Final.jsonl"

def split_steps(text):
    return [s.strip() for s in text.split("\n") if s.strip()]

def split_list(text):
    return [s.strip() for s in text.split(",") if s.strip()]

def parse_parameters(text):
    if not isinstance(text, str) or "=" not in text:
        return {}
    result = {}
    for part in text.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            result[key.strip()] = value.strip()
    return result

with open(input_csv, newline='', encoding='gb18030') as csvfile, open(output_jsonl, 'w', encoding='utf-8') as jsonlfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        user_text = row["instruction"].strip()

        assistant_dict = {
            "task_type": row["task_type"],
            "steps": split_steps(row["steps"]),
            "tools": split_list(row["tools"]),
            "key_layers": split_list(row["key_layers"]),
            "parameters": parse_parameters(row.get("parameters", ""))
        }

        # ✅ 有换行 + 有缩进的 JSON 字符串（模型输出内容），结尾加上停止符
        assistant_text = json.dumps(assistant_dict, ensure_ascii=False, indent=2) + "\n<|end_of_turn|>"

        item = {
            "messages": [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_text}
            ]
        }

        jsonlfile.write(json.dumps(item, ensure_ascii=False) + '\n')

print("✅ 转换完成：含换行与缩进的 JSONL 格式输出成功！")
