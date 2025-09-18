import csvtojsonl
import json

# === 设置文件路径 ===
input_csv = "C:/Users/90608/Desktop/总集篇/Final.csv"        # 输入 CSV 文件路径
output_jsonl = "C:/Users/90608/Desktop/总集篇/structured_messages_dataset.jsonl"   # 输出 JSONL 文件路径

# === 设置字段名（根据你 CSV 表头来）===
user_field = "user_input"       # 用户指令所在的列名
assistant_field = "model_output"  # 模型输出所在的列名

# === 转换逻辑 ===
with open(input_csv, newline='', encoding='gb18030') as csvfile, open(output_jsonl, 'w', encoding='utf-8') as jsonlfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        user_text = row[user_field].strip()
        assistant_text = row[assistant_field].strip()

        messages = {
            "messages": [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_text}
            ]
        }
        jsonlfile.write(json.dumps(messages, ensure_ascii=False) + '\n')

print("✅ 转换完成，文件已保存为 model.jsonl")
