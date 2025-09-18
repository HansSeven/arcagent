import json
from langchain_core.messages import AIMessage
from langchain.embeddings import HuggingFaceEmbeddings
"""                                      提取代码tool                                          """


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

"""                                                           向量数据库构建                                                    """
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

# 你的 tool_docs 格式
tool_docs = [
    ("Buffer_analysis", "Create buffer polygons around input features at a specified distance."),
    ("Clip_analysis", "Extract input features that fall within the boundary of clip features."),
    ("Project_management", "Transform spatial data from one coordinate system to another."),
    ("Kernel_Density", "Generate a raster surface showing the density of features in a neighborhood."),
    ("SpatialJoin_analysis", "Join attributes from one feature layer to another based on spatial relationship."),
    ("SummaryStatistics", "Summarize field values by group, producing a standalone table."),
    ("SelectLayerByAttribute", "Select features from a layer based on attribute query expressions."),
    ("GenerateNearTable_analysis", "Create a table recording the distance to nearest features."),
    ("TableToTable_conversion", "Export a table from one format or location to another."),
    ("MultipleRingBuffer_analysis", "Create multiple concentric buffer rings around features."),
    ("Erase_analysis", "Remove areas of input features that overlap with erase features."),
    ("Dissolve_management", "Aggregate features based on a common attribute to form larger units."),
    ("Identity_analysis", "Overlay two layers and append attributes of identity features to input features."),
    ("Near_analysis", "Calculate distance from each feature to the nearest feature in another layer."),
    ("Split_analysis", "Split input features into multiple outputs based on boundaries or attribute values."),
    ("FeatureToPoint_management", "Create points at the centroid or inside location of polygon features."),
    ("FeatureVerticesToPoints_management", "Convert feature vertices into individual point features."),
    ("FeatureToLine_management", "Convert input polygons or multipart features into line features.")
]

# 1. 将每个工具包装成 Document（含描述和元数据）
documents = [Document(page_content=desc, metadata={"tool_name": name}) for name, desc in tool_docs]

# 2. 加载 embedding 模型（可替换为 HuggingFaceEmbeddings 等）
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

# 3. 构建向量库
vectorstore = FAISS.from_documents(documents, embedding_model)

"""                                          匹配代码                                           """
def match_tool_names_with_rag(model_tool_names, vectorstore, k=1):
    matched_tool_names = []
    for query in model_tool_names:
        results = vectorstore.similarity_search(query, k=k)
        if results:
            matched_tool_names.append(results[0].metadata["tool_name"])
        else:
            print(f"[WARN] No match found for '{query}'")
    return matched_tool_names


"""                                         Tool_RAG_Node                                       """

def tool_rag_bind_node(state, llm, vectorstore, tool_pool, system_message, name="tool_binder"):
    """
    Node: 提取工具名 → 向量匹配 → 构建绑定 agent → 写入 state 供 analyzer 使用
    """
    # Step 1: 提取工具名
    model_tools = extract_tool_names_from_json_message(state["messages"])
    if not model_tools:
        print("[WARN] No tool names extracted from messages.")
        return {
            "messages": [AIMessage(content=json.dumps({"matched_tools": []}), name=name)],
            "sender": name,
            "analyzer_agent": None
        }

    # Step 2: RAG 匹配真实工具名
    matched_names = match_tool_names_with_rag(model_tools, vectorstore)
    if not matched_names:
        print(f"[WARN] No matches found for extracted tools: {model_tools}")

    # Step 3: 从工具池中选取定义
    selected_tools = [tool for tool in tool_pool if tool.name in matched_names]

    # Step 4: 创建绑定后的 agent
    analyzer_agent = create_agent(llm, selected_tools, system_message)

    # Step 5: 返回新的状态，供 analyzer 节点使用
    return {
        "messages": [AIMessage(content=json.dumps({"matched_tools": matched_names}), name=name)],
        "sender": name,
        "analyzer_agent": analyzer_agent
    }


