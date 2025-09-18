from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, set_seed
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import torch

# ==== 固定随机种子 ====
set_seed(42)

# ==== 路径配置 ====
model_path = "/run/media/test/desk2/hans7/openchat-3.5-1210"
train_file = "/run/media/test/desk2/hans7/structured_messages_dataset.jsonl"
output_dir = "/run/media/test/desk2/hans7/openchat_lora_output"

assert torch.cuda.is_available(), "GPU not available. Check CUDA environment."

# ==== 加载 tokenizer 和模型 ====
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
# ✅ 设置停止符号为你数据中添加的 <|endofassistant|>
tokenizer.add_special_tokens({"eos_token": "<|endofassistant|>"})
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

# ==== 关键修复：使输入可反向传播（适配 gradient_checkpointing）====
if hasattr(model, "enable_input_require_grads"):
    model.enable_input_require_grads()

# ==== 配置 LoRA ====
peft_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, peft_config)
model.resize_token_embeddings(len(tokenizer))
# ==== 打印可训练参数（确认 LoRA 激活） ====
print(">>>>> 可训练参数信息：")
model.print_trainable_parameters()

# ==== 数据加载与预处理 ====
def format_chat(example):
    messages = example["messages"]
    text = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"].strip()
        if role == "user":
            text += f"<|user|>\n{content}\n"
        elif role == "assistant":
            text += f"<|assistant|>\n{content}\n"
    example["text"] = text
    return example

raw_dataset = load_dataset("json", data_files={"train": train_file}, split="train")
dataset = raw_dataset.map(format_chat)

def tokenize(example):
    tokens = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )
    tokens["labels"] = [
        tid if tid != tokenizer.pad_token_id else -100
        for tid in tokens["input_ids"]
    ]
    return tokens

dataset = dataset.map(tokenize, remove_columns=dataset.column_names)
dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

print(f">>>>> 数据集总条数: {len(dataset)}")

# ==== 训练参数配置 ====
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,  # 等效 batch=8
    num_train_epochs=3,
    learning_rate=2e-4,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    fp16=True,
    logging_strategy="steps",
    logging_steps=10,
    eval_strategy="no",
    save_strategy="epoch",
    save_total_limit=2,
    output_dir=output_dir,
    remove_unused_columns=False,
    report_to="none",
    gradient_checkpointing=True,
    logging_dir=f"{output_dir}/logs"
)

# ==== 创建 Trainer ====
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=None  # 使用已有字段，无需额外 collator
)

# ==== 开始训练 ====
print(">>>>> 开始训练 LoRA 微调模型...")
trainer.train()
print(">>>>> 训练完成！")

# ==== 保存结果 ====
print(">>>>> 正在保存模型...")
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
trainer.state.save_to_json(f"{output_dir}/trainer_state.json")
print(">>>>> 模型和训练状态已保存到:", output_dir)
