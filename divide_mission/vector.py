from tool_docs import tool_docs
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def extract_tool_names_from_json_message(messages):
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            try:
                data = json.loads(msg.content)
                if isinstance(data, dict) and "tools" in data:
                    return data["tools"]
            except json.JSONDecodeError:
                continue
    return []

# 1. 将每个工具包装成 Document（含描述和元数据）
documents = [Document(page_content=f"Tool Name: {name}\nFunction: {desc}",metadata={"tool_name": name}) for name, desc in tool_docs]

# 2. 加载 embedding 模型（可替换为 HuggingFaceEmbeddings 等）
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# 3. 构建向量库
vectorstore1 = FAISS.from_documents(documents, embedding_model)

vectorstore1.save_local("my_vectorstore")