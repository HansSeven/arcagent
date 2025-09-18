# tools/hello.py
from base import register_tool

@register_tool(
    name="hello",
    description="Say hello to someone",
    input_schema={
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"]
    }
)
def hello_handler(args):
    name = args["name"]
    return {
        "content": [{"type": "text", "text": f"Hello, {name}!"}],
        "is_error": False
    }
