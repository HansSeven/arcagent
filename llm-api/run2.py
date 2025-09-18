import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# ==== 路径配置 ====
base_model_path = "/run/media/test/desk2/hans7/openchat-3.5-1210"
lora_adapter_path = "/run/media/test/desk2/hans7/openchat_lora_output"
csv_path = "/run/media/test/desk2/hans7/不公平对决数据集.csv"  # 输入CSV
output_csv = "/run/media/test/desk2/hans7/unfair/unf.csv"          # 输出CSV

# ==== 加载 tokenizer（记得加 pad_token）====
tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
tokenizer.add_special_tokens({"pad_token": "<|pad|>"})  # 和训练保持一致

# ==== 加载 base model + 扩展词表 ====
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)
base_model.resize_token_embeddings(len(tokenizer))  # 对齐 adapter 的词表大小

# ==== 加载 LoRA adapter ====
model = PeftModel.from_pretrained(base_model, lora_adapter_path)
model.eval()

# ==== 读取 CSV 数据 ====
df = pd.read_csv(csv_path)
results = []

# ==== 推理每一条指令 ====
for idx, row in df.iterrows():
    instruction = row["instruction"]
    prompt = f"<|user|>\n{instruction}\n<|assistant|>\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            top_p=0.9  # 🚫 移除 temperature，避免警告
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 存储结果
    results.append({
        "instruction": instruction,
        "model_response": response
    })
    print(f"✅ 样本 {idx + 1} 生成完成")

# ==== 写入输出 CSV ====
pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")
print(f"\n🎉 所有指令处理完毕，结果已保存到：{output_csv}")
