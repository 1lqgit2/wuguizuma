"""dump Unity prefab/scene UGUI tree with RectTransform geometry.
usage: python ugui_dump.py <file> [--all]
"""
import re, io, sys

def parse(path):
    s = io.open(path, encoding="utf-8").read()
    docs = {}
    order = []
    for chunk in re.split(r'(?m)^--- ', s)[1:]:
        head = chunk.split("\n", 1)[0]
        m = re.match(r'!u!(\d+) &(-?\d+)( stripped)?', head)
        if not m:
            continue
        fid = m.group(2)
        docs[fid] = {"cls": m.group(1), "body": "--- " + chunk, "stripped": bool(m.group(3))}
        order.append(fid)
    return s, docs, order

def field(doc, key, default=""):
    m = re.search(r'\n  ' + re.escape(key) + r': (.*)', doc["body"])
    return m.group(1).strip() if m else default

def vec(txt):
    nums = re.findall(r'-?\d+\.?\d*(?:e-?\d+)?', txt)
    return [float(n) for n in nums] if nums else []

def dump(path, show_all=True):
    s, docs, order = parse(path)
    # GameObject name map
    go_name = {}
    for fid, d in docs.items():
        if d["cls"] == "1":
            go_name[fid] = field(d, "m_Name")
    # RT -> GO
    rt_go = {}
    for fid, d in docs.items():
        if d["cls"] in ("224", "4"):
            g = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', d["body"])
            rt_go[fid] = g.group(1) if g else None
    # component -> GO and GO -> components
    comp_go = {}
    go_comp = {}
    for fid, d in docs.items():
        if d["cls"] in ("1",):
            for m in re.finditer(r'- component: \{fileID: (-?\d+)\}', d["body"]):
                go_comp.setdefault(fid, []).append(m.group(1))
                comp_go[m.group(1)] = fid
    # parent relations from RT
    father = {}
    children = {}
    for fid, d in docs.items():
        if d["cls"] != "224":
            continue
        f = re.search(r'm_Father: \{fileID: (-?\d+)\}', d["body"])
        father[fid] = f.group(1) if f else None
        for m in re.finditer(r'- \{fileID: (-?\d+)\}', d["body"].split("m_Children:")[1] if "m_Children:" in d["body"] else ""):
            children.setdefault(fid, []).append(m.group(1))

    def label(rtid):
        gid = rt_go.get(rtid)
        nm = go_name.get(gid, "?")
        act = field(docs[gid], "m_IsActive") if gid in docs else "?"
        return "%s [%s] rt=%s go=%s active=%s" % (nm, docs[rtid]["cls"], rtid, gid, act)

    def walk(rtid, depth=0):
        d = docs[rtid]
        print("  " * depth + label(rtid))
        am, ax = vec(field(d, "m_AnchorMin")), vec(field(d, "m_AnchorMax"))
        pos, size = vec(field(d, "m_AnchoredPosition")), vec(field(d, "m_SizeDelta"))
        piv, sc = vec(field(d, "m_Pivot")), vec(field(d, "m_LocalScale"))
        print("  " * depth + "   anchor %s~%s pos %s size %s pivot %s scale %s" % (
            am, ax, pos, size, piv, sc))
        gid = rt_go.get(rtid)
        for cid in go_comp.get(gid, []):
            c = docs.get(cid)
            if not c:
                continue
            if c["cls"] == "114":
                sc_ = field(c, "m_Script")
                gm = re.search(r'guid: (\w+)', sc_)
                extra = ""
                if gm and gm.group(1) == "fe87c0e1cc204ed48ad3b37840f39efc":
                    extra = "Image sprite=%s color=%s type=%s" % (
                        field(c, "m_Sprite")[:34], field(c, "m_Color"), field(c, "m_Type"))
                elif gm and gm.group(1) == "5f7201a12d95ffc409449d95f23cf332":
                    extra = "Text '%s' size=%s font=%s color=%s" % (
                        field(c, "m_Text")[:30], field(c, "m_FontSize"),
                        field(c, "m_FontData")[:0] or "", field(c, "m_Color"))
                elif gm and gm.group(1) == "4e29b1a8efbd4b44bb3f3716e73f07ff":
                    calls = re.findall(r'm_MethodName: (.*)', c["body"])
                    tgts = re.findall(r'm_Target: \{fileID: (-?\d+)\}', c["body"])
                    extra = "Button calls=%s targets=%s" % (calls, tgts)
                elif gm and gm.group(1) == "0cd44c1031e13a943bb63640046fad76":
                    extra = "CanvasScaler mode=%s ref=%s match=%s" % (
                        field(c, "m_UiScaleMode"), field(c, "m_ReferenceResolution"),
                        field(c, "m_MatchWidthOrHeight"))
                elif gm:
                    extra = "Mono " + gm.group(1)
                print("  " * depth + "   - " + extra)
            elif c["cls"] == "223":
                print("  " * depth + "   - Canvas renderMode=%s" % field(c, "m_RenderMode"))
        for ch in children.get(rtid, []):
            if ch in docs:
                walk(ch, depth + 1)

    roots = [fid for fid in order if docs[fid]["cls"] == "224" and father.get(fid) in (None, "0")]
    for r in roots:
        walk(r)

if __name__ == "__main__":
    dump(sys.argv[1])
