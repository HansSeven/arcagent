import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from collections import Counter

# ==== 修改为你的模型路径 ====
model_path = "/run/media/test/desk2/hans7/openchat-3.5-1210"

# ==== 加载模型 ====
print(">> 正在加载模型（仅加载结构，不显存分配）...")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="cpu",  # 避免占用显存
)

# ==== 收集参数名 ====
print(">> 收集模型参数名并筛选可能适用于 LoRA 的模块...")
candidate_keywords = ["q", "k", "v", "proj", "linear", "gate", "attn"]
layer_name_counter = Counter()

for name, param in model.named_parameters():
    for key in candidate_keywords:
        if key in name.lower():
            layer_parts = name.split(".")
            for part in layer_parts:
                if any(k in part.lower() for k in candidate_keywords):
                    layer_name_counter[part] += 1

# ==== 显示可能的 LoRA 插入模块名 ====
print("\n>> ✅ 推荐的 target_modules 候选（按出现频率排序）：\n")
for name, count in layer_name_counter.most_common():
    print(f"  {name:30} ⟶  出现 {count} 次")

print("\n>> ✅ 你可以将这些名称中的 2~6 个常见项作为 target_modules，尝试挂载 LoRA。")
