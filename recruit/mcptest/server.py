#!/usr/bin/env python3
import sys, json
import tools  # 导入后自动完成所有工具注册
from tools.base import list_tools, call_tool

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        mid = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "tools/list":
            send({"jsonrpc":"2.0","id":mid,"result":{"tools": list_tools()}})
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            result = call_tool(name, arguments)
            send({"jsonrpc":"2.0","id":mid,"result": result})
        else:
            send({"jsonrpc":"2.0","id":mid,"error":{"code":-32601,"message":"Method not found"}})

if __name__ == "__main__":
    main()
