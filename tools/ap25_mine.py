# -*- coding: utf-8 -*-
# AP25Defs.luac 粗提取：LuaR 5.1 字节码里的字符串常量（unluac 失败则直接扫字符串池）
import re, collections, os
p = r"Children of the Light\Resources\ContentPackages\AP25Defs.lua.luac"
d = open(p, "rb").read()
print("大小:", len(d))
# Lua 5.1 chunk: 头之后各函数 upvalue/name 常量。直接扫 >=4 可读串
strs = re.findall(rb'[\x20-\x7e]{4,}', d)
seen = []
for s in strs:
    t = s.decode()
    if t not in seen:
        seen.append(t)
print("唯一串数:", len(seen))
for t in seen:
    print("  ", t[:120])
