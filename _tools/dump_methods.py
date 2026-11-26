import sys
import dnfile

ELEM = {
    0x01: "void", 0x02: "bool", 0x03: "char", 0x04: "i1", 0x05: "u1",
    0x06: "i2", 0x07: "u2", 0x08: "int32", 0x09: "uint32", 0x0A: "int64",
    0x0B: "uint64", 0x0C: "float32", 0x0D: "float64", 0x0E: "string",
    0x0F: "ptr", 0x10: "byref", 0x11: "valuetype", 0x12: "class",
    0x13: "var", 0x14: "array", 0x15: "genericinst", 0x16: "typedbyref",
    0x18: "intptr", 0x19: "uintptr", 0x1C: "object",
}


def read_compressed(b, i):
    x = b[i]
    if x & 0x80 == 0:
        return x, i + 1
    if x & 0xC0 == 0x80:
        return ((x & 0x3F) << 8) | b[i + 1], i + 2
    return ((x & 0x1F) << 24) | (b[i + 1] << 16) | (b[i + 2] << 8) | b[i + 3], i + 4


def sig_summary(blob):
    if not blob:
        return "?"
    b = bytes(blob)
    i = 1  # skip calling convention
    if b[0] & 0x10:  # generic
        _, i = read_compressed(b, i)
    n, i = read_compressed(b, i)
    if i >= len(b):
        return "?"
    ret = ELEM.get(b[i], hex(b[i]))
    return ret


def methods_of(path, type_name):
    pe = dnfile.dnPE(path)
    if not pe.net or not pe.net.mdtables:
        return None
    md = pe.net.mdtables
    typedefs = md.TypeDef.rows
    methods = md.MethodDef.rows
    starts = [(i, t.TypeName, t.MethodList[0].row_index if t.MethodList else 0)
              for i, t in enumerate(typedefs)]
    out = []
    for idx, (i, name, start_rid) in enumerate(starts):
        if name != type_name:
            continue
        end_rid = starts[idx + 1][2] if idx + 1 < len(starts) else len(methods) + 1
        for rid in range(start_rid, end_rid):
            if 1 <= rid <= len(methods):
                m = methods[rid - 1]
                if str(m.Name).startswith("op_"):
                    out.append((str(m.Name), sig_summary(m.Signature.value)))
    return out


if __name__ == "__main__":
    type_name = sys.argv[1]
    for path in sys.argv[2:]:
        res = methods_of(path, type_name)
        print("=" * 16, path)
        if res is None:
            print("   无元数据")
            continue
        if not res:
            print("   没有运算符 / 没找到类型")
        for name, ret in res:
            print(f"   {name:14s} -> {ret}")
