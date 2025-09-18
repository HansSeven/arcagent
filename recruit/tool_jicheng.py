import os, json, time
from typing import Any, Dict
from dashscope import Generation


# ===== 1) 定义“工具”：描述 + 真正的Python实现 =====
# （A）工具的“说明书”（给模型看的，JSON Schema）
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city in Celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. Beijing"},
                },
                "required": ["city"],
                "additionalProperties": False
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_add",
            "description": "Add two numbers and return the sum.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    }
]

# （B）工具的“真实实现”（给你本地/后端用的）
def get_weather(city: str) -> Dict[str, Any]:
    # 这里演示用“假数据”，实际可改成 HTTP/RPC 查询
    mock = {
        "Beijing": {"temperature": 27.2, "description": "sunny"},
        "上海": {"temperature": 29.0, "description": "cloudy"},
    }
    data = mock.get(city, {"temperature": 25.0, "description": "unknown"})
    return {"city": city, **data}

def calc_add(a: float, b: float) -> Dict[str, Any]:
    return {"a": a, "b": b, "sum": float(a) + float(b)}

# 工具分发器
TOOL_IMPL = {
    "get_weather": lambda args: get_weather(**args),
    "calc_add":    lambda args: calc_add(**args),
}


# ===== 2) 一个helper：调用Qwen并返回message对象 =====
def qwen_call(messages, tools=None, tool_choice="auto", model="qwen-plus"):
    # tool_choice: "auto" 交给模型决定是否/调用哪个工具
    resp = Generation.call(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        result_format="message"  # 返回OpenAI风格的messages对象
    )
    # 取出标准message（role/content/tool_calls等）
    return resp["output"]["choices"][0]["message"]


# ===== 3) 一个完整的“工具调用循环” =====
def run_dialog(user_query: str):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when helpful."},
        {"role": "user",   "content": user_query}
    ]

    # 第一次调用：模型可能返回普通文本，或者提出 tool_calls
    assistant_msg = qwen_call(messages, tools=TOOLS_SPEC, tool_choice="auto")
    messages.append(assistant_msg)

    # 如果有工具调用，逐个执行，然后把结果喂回去，再次让模型总结
    tool_calls = assistant_msg.get("tool_calls") or []
    for tc in tool_calls:
        # Qwen通常与OpenAI类似：tc包含 id/type/function{name,arguments(str或obj)}
        fn = tc.get("function", {})
        name = fn.get("name")
        raw_args = fn.get("arguments")

        # arguments 可能是字符串也可能是对象，这里统一成 dict
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {}
        else:
            args = raw_args or {}

        # 执行本地/后端工具
        print(f"[Tool Invoke] {name}({args})")
        executor = TOOL_IMPL.get(name)
        if executor is None:
            tool_result = {"error": f"unknown tool: {name}"}
        else:
            try:
                tool_result = executor(args)
            except Exception as e:
                tool_result = {"error": str(e)}

        print(f"[Tool Result] {tool_result}")

        # 把工具结果作为“tool消息”喂回去
        # Qwen基本兼容OpenAI的tool消息格式：包含 tool_call_id / name / content
        messages.append({
            "role": "tool",
            "tool_call_id": tc.get("id", ""),
            "name": name,
            "content": json.dumps(tool_result, ensure_ascii=False)
        })

    # 若发生了工具调用，再让模型基于工具结果给最终答案
    if tool_calls:
        final_msg = qwen_call(messages, tools=TOOLS_SPEC, tool_choice="none")
        messages.append(final_msg)
        return final_msg["content"]

    # 没有工具调用，直接返回上一次assistant输出
    return assistant_msg.get("content", "")


if __name__ == "__main__":
    # 示例1：会触发天气工具
    print(">>> Q1")
    ans = run_dialog("今天北京的气温和天气如何？")
    print("Assistant:", ans, "\n")

    # 示例2：会触发计算工具
    print(">>> Q2")
    ans = run_dialog("请计算 12.5 + 7.25 等于多少，并给出简短说明。")
    print("Assistant:", ans, "\n")

    # 示例3：普通闲聊（一般不触发工具）
    print(">>> Q3")
    ans = run_dialog("你好呀！")
    print("Assistant:", ans, "\n")
