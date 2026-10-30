import base64, json
payload = r'''
import idaapi, idc, idautils, ida_bytes
# find "MOVE\0LOADK" style opcode name table
results = []
for s, e, name in [(0x0, 0, 'x')]:
    pass
# search in all segments for b"MOVE\x00LOADK\x00"
import ida_segment
seg = ida_segment.get_first_seg()
hits = []
pattern = b"MOVE\x00LOADK\x00LOADKX\x00"
n = ida_segment.get_segm_qty()
for i in range(n):
    sg = ida_segment.getnseg(i)
    start = sg.start_ea; end = sg.end_ea
    data = ida_bytes.get_bytes(start, min(end-start, 0x2000000))
    if not data: continue
    idx = data.find(pattern)
    if idx >= 0:
        hits.append((start+idx, hex(start)))
print("HITS", hits)
for ea, segname in hits:
    # dump following strings
    p = ea
    names = []
    for _ in range(50):
        q = p
        while ida_bytes.get_byte(q) != 0:
            q += 1
        nm = ida_bytes.get_bytes(p, q-p).decode()
        names.append(nm)
        p = q+1
        if len(names) > 40: break
    print(names)
'''
b64 = base64.b64encode(payload.encode()).decode()
import urllib.request
def mcp_call(tool, args):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":tool,"arguments":args}}).encode()
    req = urllib.request.Request("http://127.0.0.1:13337/mcp", data=body, headers={"Content-Type":"application/json"})
    r = urllib.request.urlopen(req, timeout=120)
    return r.read().decode()
print(mcp_call("py_eval", {"code": b64}))
