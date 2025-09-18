#!/usr/bin/env python3
import sys, json   # 导入系统输入输出和 JSON 库

# 一个小函数：负责把响应打印回去（就是“回消息”）
def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

# 循环：不停地等“客户端/Agent”发来的消息
for line in sys.stdin:
    # 把收到的一行字符串转成 JSON 对象
    request = json.loads(line)

    # 取出请求里的 id（用来对应请求和响应）
    req_id = request.get("id")

    # 如果 Agent 想“列出有哪些工具”
    if request["method"] == "tools/list":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [{
                    "name": "hello",             # 工具的名字
                    "description": "打招呼工具",  # 工具干啥的
                    "input_schema": {            # 输入参数定义
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                }]
            }
        })

    # 如果 Agent 想“调用某个工具”
    elif request["method"] == "tools/call":
        args = request["params"]["arguments"]  # 拿到调用传来的参数
        user_name = args["name"]

        # 返回执行结果（这里就是拼一句话）
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{
                    "type": "text",
                    "text": f"Hello, {user_name}!"
                }],
                "is_error": False
            }
        })
