import base64, json, urllib.request
payload = open(r'd:\新建文件夹\LightEncounters\tools\ida_payload.py').read()
b64 = base64.b64encode(payload.encode()).decode()
code = f'import base64; exec(base64.b64decode("{b64}").decode())'
def mcp_call(tool, args):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":tool,"arguments":args}}).encode()
    req = urllib.request.Request("http://127.0.0.1:13337/mcp", data=body, headers={"Content-Type":"application/json"})
    r = urllib.request.urlopen(req, timeout=300)
    return json.loads(r.read().decode())
res = mcp_call("py_eval", {"code": code})
txt = res["result"]["content"][0]["text"]
d = json.loads(txt)
print(d.get("stdout", ""))
print(d.get("stderr", "")[:2000])
