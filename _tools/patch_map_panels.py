# -*- coding: utf-8 -*-
"""把 Map 场景里的 cebianPanel / AdConfirm 从 Footer 下面挪到 Canvas(MainUI) 下，
并清掉 AdConfirm 实例上残留的 20 条根 RectTransform 覆盖（含 90 度旋转）。"""
import io, re

P = "Assets/_Scenes/Map.unity"
s = io.open(P, encoding="utf-8").read()
orig = s

CANVAS = "1790492667549795203"   # MainUI / Canvas
FOOTER = "1790492667549796708"   # 之前的错误父级
AD = "1458445511"                # AdConfirm PrefabInstance
CE = "1970268267"                # cebianPanel PrefabInstance
AD_RT = "1458445512"             # AdConfirm 实例的 stripped RectTransform
CE_RT = "1970268268"             # cebianPanel 实例的 stripped RectTransform
AD_ROOT_RT = "3639414679521888923"

# ---------- 1. 两个实例改父 ----------
for pid in (AD, CE):
    i = s.index("--- !u!1001 &" + pid)
    j = s.find("\n--- ", i + 10)
    blk = s[i:j]
    oldline = "    m_TransformParent: {fileID: %s}" % FOOTER
    assert blk.count(oldline) == 1, (pid, "parent")
    blk = blk.replace(oldline, "    m_TransformParent: {fileID: %s}" % CANVAS, 1)
    s = s[:i] + blk + s[j:]
print("1) 两个实例已挂到 Canvas 下")

# ---------- 2. Footer 子列表里摘掉 ----------
i = s.index("--- !u!224 &" + FOOTER)
j = s.find("\n--- ", i + 10)
blk = s[i:j]
for rt in (AD_RT, CE_RT):
    line = "  - {fileID: %s}\n" % rt
    assert blk.count(line) == 1, (rt, "footer child")
    blk = blk.replace(line, "", 1)
s = s[:i] + blk + s[j:]
print("2) Footer 子列表已移除两个面板")

# ---------- 3. Canvas 子列表末尾追加（最上层） ----------
i = s.index("--- !u!224 &" + CANVAS)
j = s.find("\n--- ", i + 10)
blk = s[i:j]
anchor = "  - {fileID: %s}\n" % FOOTER
assert blk.count(anchor) == 1, "canvas child"
blk = blk.replace(anchor, anchor + "  - {fileID: %s}\n  - {fileID: %s}\n" % (AD_RT, CE_RT), 1)
s = s[:i] + blk + s[j:]
print("3) Canvas 子列表已追加（渲染在其它 UI 之上）")

# ---------- 4. 删除 AdConfirm 根 RT 的 20 条覆盖 ----------
i = s.index("--- !u!1001 &" + AD)
j = s.find("\n--- ", i + 10)
blk = s[i:j]
pat = re.compile(
    r'    - target: \{fileID: ' + AD_ROOT_RT + r', guid: 590c0561156c3394a8cf3c487b0d4cc2,\n'
    r'        type: 3\}\n'
    r'      propertyPath: (?:m_Pivot\.[xy]|m_AnchorMax\.[xy]|m_AnchorMin\.[xy]|m_SizeDelta\.[xy]|'
    r'm_LocalPosition\.[xyz]|m_LocalRotation\.[wxyz]|m_AnchoredPosition\.[xy]|m_LocalEulerAnglesHint\.[xyz])\n'
    r'      value: [^\n]*\n'
    r'      objectReference: \{fileID: 0\}\n')
blk2, n = pat.subn("", blk)
assert n == 20, n
s = s[:i] + blk2 + s[j:]
print("4) AdConfirm 根 RT 覆盖已删除", n, "条")

assert s != orig
io.open(P, "w", encoding="utf-8", newline="\n").write(s)

# ---------- 校验 ----------
s2 = io.open(P, encoding="utf-8").read()
ids = re.findall(r'(?m)^--- !u!\d+ &(-?\d+)', s2)
dup = [x for x in set(ids) if ids.count(x) > 1]
print("docs", len(ids), "dup", dup)
for pid in (AD, CE):
    i = s2.index("--- !u!1001 &" + pid)
    j = s2.find("\n--- ", i + 10)
    blk = s2[i:j]
    print(pid, "parent =", re.search(r'm_TransformParent: \{fileID: (-?\d+)\}', blk).group(1),
          "| mods", blk.count("    - target:"))
m = re.search(r'--- !u!224 &' + CANVAS + r'\n(.*?)(?=\n--- )', s2, re.S)
kids = re.findall(r'- \{fileID: (\d+)\}', m.group(1)[m.group(1).index("m_Children:"):m.group(1).index("m_Father:")])
print("Canvas kids:", kids)
m = re.search(r'--- !u!224 &' + FOOTER + r'\n(.*?)(?=\n--- )', s2, re.S)
kids2 = re.findall(r'- \{fileID: (\d+)\}', m.group(1)[m.group(1).index("m_Children:"):m.group(1).index("m_Father:")])
print("Footer 还留着面板?", AD_RT in kids2, CE_RT in kids2, "| kid count", len(kids2))
