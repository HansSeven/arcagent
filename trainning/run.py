from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# 路径配置
base_model_path = "/run/media/test/desk2/hans7/openchat-3.5-1210"
lora_adapter_path = "/run/media/test/desk2/hans7/openchat_lora_output"

# 加载 tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)

# 加载 base 模型
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

# 加载微调后的 LoRA adapter
model = PeftModel.from_pretrained(base_model, lora_adapter_path)
model.eval()

# 编写推理 prompt
prompt = "<|user|>\nFind suitable land for community centers in areas underserved by restaurants, clinics, and transit.\n<|assistant|>\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# 推理生成
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n=== 模型输出 ===\n")
print(response)
