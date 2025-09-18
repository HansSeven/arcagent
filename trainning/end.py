from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("/run/media/test/desk2/hans7/openchat-3.5-1210", trust_remote_code=True)

print("当前结束符（字符串）:", tokenizer.eos_token)
