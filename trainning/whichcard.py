import os
import torch

print("🟢 当前环境变量 CUDA_VISIBLE_DEVICES =", os.environ.get("CUDA_VISIBLE_DEVICES", "（未设置，全部可见）"))

visible_count = torch.cuda.device_count()
print(f"🧭 当前 PyTorch 可见 GPU 数量：{visible_count}")

for i in range(visible_count):
    name = torch.cuda.get_device_name(i)
    print(f"  🔹 PyTorch 中的 cuda:{i} -> {name}")
