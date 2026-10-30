# -*- coding: utf-8 -*-
# tgcl_probe3.py: 验证 segD ref 是否为字符串哈希
import struct, re, zlib, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
o = struct.unpack_from("<5I", d, 24)
o1, o2, o3, o4, o5 = o
segC = d[o3:o4]; segD = d[o4:o5]

strs = [s for s in segC.split(b"\x00") if s]

def fnv1(b):
    h = 0x811c9dc5
    for x in b: h = ((h ^ x) * 0x01000193) & 0xffffffff
    return h
def fnv1a(b):
    h = 0x811c9dc5
    for x in b: h = ((h * 0x01000193) ^ x) & 0xffffffff
    return h
def djb2(b):
    h = 5381
    for x in b: h = (h * 33 + x) & 0xffffffff
    return h
def jhash(b):
    h = 0
    for x in b: h = (h * 31 + x) & 0xffffffff
    return h

hashsets = {
    "crc32": {zlib.crc32(s) for s in strs},
    "fnv1": {fnv1(s) for s in strs},
    "fnv1a": {fnv1a(s) for s in strs},
    "djb2": {djb2(s) for s in strs},
    "java31": {jhash(s) for s in strs},
}

# 收集 segD refs（同 probe2 方式）
name_re = re.compile(rb"BstNode_(\d+)\x00")
refs = []; i = 0
while True:
    m = name_re.search(segD, i)
    if not m: break
    p = m.end()
    if p + 4 <= len(segD):
        cnt = struct.unpack_from("<I", segD, p)[0]
        if 0 < cnt < 64 and p + 4 + 4*cnt + 4 <= len(segD):
            refs += list(struct.unpack_from(f"<{cnt}I", segD, p+4))
            i = p + 4 + 4*cnt
            continue
    i = m.end()
us = set(refs)
print("unique refs:", len(us))
for name, hs in hashsets.items():
    inter = us & hs
    print(f" {name}: match {len(inter)}/{len(us)} unique refs ({100*len(inter)/len(us):.1f}%)")
# 也对整个 segD 全部 u32 测
allu = set(struct.unpack_from(f"<{len(segD)//4}I", segD, 0))
for name, hs in hashsets.items():
    print(f" all-u32 {name}: {len(allu & hs)}")
