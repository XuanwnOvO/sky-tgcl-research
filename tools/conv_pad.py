import sys, io
sys.path.insert(0, r'd:\新建文件夹\LightEncounters\tools')
import struct

# monkey-patch maxstack to add slack before importing convert usage
import tgc2std
orig_emit = tgc2std.emit_proto
def emit_proto(w, p, top):
    p = dict(p)
    p['maxstack'] = p['maxstack'] + 8
    orig_emit(w, p, top)
tgc2std.emit_proto = emit_proto
tgc2std.convert(sys.argv[1], sys.argv[2])
print('converted')
