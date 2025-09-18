from langchain_core.messages import AIMessage
import json
from agent_builder import create_agent

def extract_tool_names_from_messages(messages):
    """从 messages 中倒序提取第一个合法的 JSON 串，并解析其中的 tools"""
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            try:
                data = json.loads(msg.content)
                if isinstance(data, dict) and "tools" in data:
                    return data["tools"]
            except json.JSONDecodeError:
                continue
    return []

def tool_select_bind_node(state, llm, tool_pool, system_message, name="tool_rag"):
    """
    作用：从 state["messages"] 中提取工具名 → 在 tool_pool 中选取定义 → bind → 返回新 agent 到 state。
    """
    # Step 1: 提取工具名（来自 messages 的 JSON 格式 content）
    model_tools = extract_tool_names_from_messages(state["messages"])
    if not model_tools:
        print("[WARN] No tool names extracted from messages.")
        return {
            "messages": [AIMessage(content=json.dumps({"matched_tools": []}), name=name)],
            "sender": name,
            "analyzer_agent": None
        }

    # Step 2: 精确匹配工具（名字完全一致）
    matched_names = [tool.name for tool in tool_pool if tool.name in model_tools]
    selected_tools = [tool for tool in tool_pool if tool.name in matched_names]
    print("[TOOL_BIND_NODE] ✅ Matched tools:", matched_names)
    # Step 3: 绑定 agent（使用你已有的 create_agent 函数）
    analyzer_agent = create_agent(llm, selected_tools, system_message)
    print("[TOOL_BIND_NODE] ✅ Analyzer agent created with tools:", [t.name for t in selected_tools])

    # Step 4: 返回更新后的状态
    return {
        "messages": [AIMessage(content=json.dumps({"matched_tools": matched_names}), name=name)],
        "sender": name,
        "analyzer_agent": analyzer_agent
    }
