# client.py
import subprocess, json

p = subprocess.Popen(
    ["python", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

def rpc(obj):
    p.stdin.write(json.dumps(obj) + "\n")
    p.stdin.flush()
    return json.loads(p.stdout.readline())

print(rpc({"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}))

print(rpc({
  "jsonrpc":"2.0","id":2,"method":"tools/call",
  "params":{"name":"hello","arguments":{"name":"Alice"}}
}))

print(rpc({
  "jsonrpc":"2.0","id":3,"method":"tools/call",
  "params":{"name":"kb.search","arguments":{"query":"灰度发布 回滚 方案","top_k":3}}
}))

print(rpc({
  "jsonrpc":"2.0","id":4,"method":"tools/call",
  "params":{"name":"gis.buffer","arguments":{"input_layer":"roads.shp","distance":"1000 m","dissolve":True}}
}))
