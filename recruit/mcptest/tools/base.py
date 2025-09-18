# tools/base.py
from typing import Callable, Dict, Any

REGISTRY: Dict[str, Dict[str, Any]] = {}

def register_tool(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
):
    """装饰器：登记工具的元数据 + 处理函数"""
    def deco(func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        if name in REGISTRY:
            raise ValueError(f"Duplicate tool name: {name}")
        REGISTRY[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "handler": func,
        }
        return func
    return deco

def list_tools():
    """返回 MCP 规范的工具清单"""
    return [
        {
            "name": meta["name"],
            "description": meta["description"],
            "input_schema": meta["input_schema"],
        }
        for meta in REGISTRY.values()
    ]

def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """调用具体工具处理函数，统一异常转为 is_error"""
    meta = REGISTRY.get(name)
    if not meta:
        return _err(f"Unknown tool: {name}")
    try:
        return meta["handler"](arguments)  # 必须返回 MCP 的 result 片段
    except Exception as e:
        return _err(str(e))

def _err(msg: str) -> Dict[str, Any]:
    return {
        "content": [{"type": "text", "text": f"Error: {msg}"}],
        "is_error": True
    }
