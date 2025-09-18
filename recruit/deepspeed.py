{
  "train_micro_batch_size_per_gpu": 2,
  "gradient_accumulation_steps": 4,
  "train_batch_size": 16,

  "bf16": { "enabled": true },

  "zero_optimization": {
    "stage": 2,
    "overlap_comm": true,
    "reduce_scatter": true,
    "contiguous_gradients": true
  },

  "optimizer": {
    "type": "AdamW",
    "params": { "lr": 5e-5, "betas": [0.9, 0.999], "eps": 1e-8, "weight_decay": 0.01 }
  },

  "gradient_clipping": 1.0
}
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling

model_name = "sshleifer/tiny-gpt2"  # 超小模型，演示友好
tok = AutoTokenizer.from_pretrained(model_name)
tok.pad_token = tok.eos_token

# 小数据示例：wikitext的很小子集
ds = load_dataset("wikitext", "wikitext-2-raw-v1")
def tok_fn(ex):
    return tok(ex["text"], truncation=True, max_length=128)
ds_tok = ds.map(tok_fn, batched=True, remove_columns=["text"])
collator = DataCollatorForLanguageModeling(tok, mlm=False)

model = AutoModelForCausalLM.from_pretrained(model_name)

args = TrainingArguments(
    output_dir="./ckpt",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    logging_steps=10,
    save_steps=1000,
    fp16=False,  # A100/H100可用 bf16；普通显卡就关掉
    bf16=True,   # 如果显卡支持 bf16 就开，和 ds_config 匹配
    deepspeed="ds_config.json",  # 关键：启用 DeepSpeed
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=ds_tok["train"].select(range(1000)),  # 取前1000行示例
    eval_dataset=ds_tok["validation"].select(range(200)),
    data_collator=collator
)

trainer.train()
"""
deepspeed train_hf_trainer.py
# 或者（多卡）
deepspeed --num_gpus=2 train_hf_trainer.py
训练
"""
import torch, deepspeed
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer

model_id = "facebook/opt-6.7b"  # 换成你的模型
tok = AutoTokenizer.from_pretrained(model_id)
tok.pad_token = tok.eos_token

# 1) 先按 HF 方式加载
hf_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True
)

# 2) 用 DeepSpeed 接管推理 (mp_size=2 表示2卡张量并行)
engine = deepspeed.init_inference(
    hf_model,
    mp_size=2,                 # 张量并行卡数；单卡就设 1
    dtype=torch.float16,       # 或 bfloat16（A100/H100）
    replace_method="auto",     # 自动注入优化的Transformer内核
    replace_with_kernel_inject=True
)

# 3) 像 HF 一样调用，只是用 engine.module 取代原 model
prompt = "Hello, how are you?"
inputs \
    = tok(prompt, return_tensors="pt").to(device="cuda")
streamer = TextStreamer(tok, skip_special_tokens=True)

with torch.inference_mode():
    _ = engine.module.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=False,
        streamer=streamer   # 流式输出（可选）
    )


"""
用官方框架：DeepSpeed-MII（Model Inferencing Interface）基于 DeepSpeed-Inference，提供现成的 HTTP/gRPC 部署能力。
服务这一块
"""
