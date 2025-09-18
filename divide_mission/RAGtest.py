from typing import Annotated, List
from langchain_core.tools import tool  # 你可能已经是 from langchain.tools 导入
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vectorstore1 = FAISS.load_local("my_vectorstore", embedding_model, allow_dangerous_deserialization=True)

def match_tool_list(queries: list[str], vectorstore=vectorstore1, k=1):
    """
    批量模糊匹配工具名称：输入一组模糊工具名，返回匹配到的标准工具名列表。
    如果某项匹配失败，则返回 None 占位。
    """
    matched_tools = []
    for query in queries:
        results = vectorstore.similarity_search(query, k=k)
        if results:
            matched_tools.append(results[0].metadata["tool_name"])
        else:
            print(f"[WARN] No match found for: {query}")
            matched_tools.append(None)
    return matched_tools


@tool
def MatchToolName(
    queries: Annotated[List[str], "A list of fuzzy tool names to be matched"]
) -> List[str]:
    """
    Matches fuzzy or partial tool names to standard local tool names using vector similarity search.
    """
    try:
        return match_tool_list(queries, vectorstore=vectorstore1, k=1)
    except Exception as e:
        return [f"Error during tool name matching: {repr(e)}"]








