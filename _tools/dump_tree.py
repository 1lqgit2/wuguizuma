# -*- coding: utf-8 -*-
"""轻量 UGUI 树 dump：名字/激活/尺寸/锚点/Graphic 颜色与射线，用于排查"打开了但看不见"。"""
import io, re, sys

def load(path):
    s = io.open(path, encoding="utf-8", errors="ignore").read()
    docs = {}
    for c in re.split(r'(?m)^--- ', s)[1:]:
        m = re.match(r'!u!(\d+) &(-?\d+)', c)
        if m:
            docs[m.group(2)] = (m.group(1), "--- " + c)
    return docs

def dump(path):
    d = load(path)
    name, rtgo, father, kids = {}, {}, {}, {}
    for k, (cls, b) in d.items():
        if cls == "1":
            m = re.search(r'\n  m_Name: (.*)', b)
            name[k] = m.group(1).strip() if m else ""
    for k, (cls, b) in d.items():
        if cls in ("224", "4"):
            m = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', b)
            rtgo[k] = m.group(1) if m else None
    for k, (cls, b) in d.items():
        if cls in ("224", "4"):
            m = re.search(r'm_Father: \{fileID: (-?\d+)\}', b)
            father[k] = m.group(1) if m else "0"
            seg = b.split("m_Children:")[1].split("m_Father:")[0] if "m_Children:" in b else ""
            kids[k] = re.findall(r'fileID: (-?\d+)', seg)

    def fld(b, kk):
        m = re.search(r'\n  ' + kk + r': (.*)', b)
        return m.group(1).strip() if m else ""

    def info(rtid):
        b = d[rtid][1]
        gid = rtgo.get(rtid)
        comps = []
        if gid and gid in d:
            for m in re.finditer(r'- component: \{fileID: (-?\d+)\}', d[gid][1]):
                c = d.get(m.group(1))
                if not c:
                    continue
                cls, bb = c
                if cls == "114":
                    gm = re.search(r'guid: (\w+)', bb)
                    g = gm.group(1) if gm else ""
                    if g == "fe87c0e1cc204ed48ad3b37840f39efc":
                        col = re.search(r'm_Color: (\{[^}]*\})', bb)
                        rt = re.search(r'm_RaycastTarget: (\d)', bb)
                        sp = re.search(r'm_Sprite: (\{[^}]*\})', bb)
                        comps.append("Image color=%s ray=%s sprite=%s" % (
                            col.group(1) if col else "?", rt.group(1) if rt else "?",
                            sp.group(1) if sp else "?"))
                    elif g == "5f7201a12d95ffc409449d95f23cf332":
                        comps.append("Text")
                    elif g == "4e29b1a8efbd4b44bb3f3716e73f07ff":
                        comps.append("Button")
                    else:
                        comps.append("Mono:" + g[:8])
                elif cls == "223":
                    comps.append("Canvas mode=%s order=%s" % (fld(bb, "m_RenderMode"), fld(bb, "m_SortingOrder")))
                elif cls == "225":
                    comps.append("CanvasGroup a=%s" % fld(bb, "m_Alpha"))
        return "anchor %s~%s pos %s size %s | %s" % (
            fld(b, "m_AnchorMin"), fld(b, "m_AnchorMax"), fld(b, "m_AnchoredPosition"),
            fld(b, "m_SizeDelta"), " ; ".join(comps))

    def walk(rtid, dep=0):
        gid = rtgo.get(rtid)
        act = ""
        if gid and gid in d:
            m = re.search(r'm_IsActive: (\d)', d[gid][1])
            act = "A" + m.group(1) if m else ""
        print("  " * dep + "- " + name.get(gid, "?") + " " + act + "  " + info(rtid))
        for c in kids.get(rtid, []):
            if c in d:
                walk(c, dep + 1)

    for k in father:
        if father[k] in ("0", None):
            walk(k)

if __name__ == "__main__":
    dump(sys.argv[1])
