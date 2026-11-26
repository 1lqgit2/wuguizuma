# -*- coding: utf-8 -*-
"""修正 cebianPanel.prefab 的面板尺寸/位置，并清理场景实例里的错位覆盖。"""
import io, re, sys

PREFAB = "Assets/AdSDK/Resources/cebianPanel.prefab"

# ---------- 目标几何（面板 520x480，底板 312x283≈1.102，误差 1.7%） ----------
BOX = "9122441691256389096"
TITLE = "6085170033539385558"
CLOSE = "2462111052324882783"
T1 = "191865702693248147"
IMA1 = "7236895754432251694"
T2 = "2072494826346800501"
IMA2 = "5932615674131030902"
GO_BTN = "4720292601761052969"
GO_TXT = "907550877877829627"

RT = {
    BOX:   {"m_AnchoredPosition": "{x: 0, y: 0}", "m_SizeDelta": "{x: 520, y: 480}"},
    TITLE: {"m_AnchoredPosition": "{x: 0, y: -38}", "m_SizeDelta": "{x: 340, y: 56}"},
    CLOSE: {"m_AnchoredPosition": "{x: -32, y: -40}", "m_SizeDelta": "{x: 64, y: 66}"},
    T1:    {"m_AnchoredPosition": "{x: 0, y: 155}", "m_SizeDelta": "{x: 480, y: 36}"},
    IMA1:  {"m_AnchoredPosition": "{x: 0, y: -74}", "m_SizeDelta": "{x: 270, y: 97}"},
    T2:    {"m_AnchoredPosition": "{x: 0, y: 0}", "m_SizeDelta": "{x: 480, y: 36}"},
    IMA2:  {"m_AnchoredPosition": "{x: 0, y: -73}", "m_SizeDelta": "{x: 270, y: 95}"},
    GO_BTN:{"m_AnchoredPosition": "{x: 0, y: -181}", "m_SizeDelta": "{x: 280, y: 97}"},
    GO_TXT:{"m_AnchoredPosition": "{x: 0, y: 0}", "m_SizeDelta": "{x: 0, y: -12}"},
}

FONTS = {  # Text 组件 fileID -> 新字号
    "2677901939638951147": 40,   # 标题 侧边栏
    "8241434830035621772": 26,   # 步骤1
    "8569781140703555311": 26,   # 步骤2
    "7817695956279352542": 26,   # 前往侧边栏
}


def split_docs(s):
    parts = re.split(r'(?m)^(--- !u!\d+ &-?\d+\n)', s)
    head = parts[0]
    docs = [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]
    return head, docs


def patch_prefab():
    s = io.open(PREFAB, encoding="utf-8").read()
    head, docs = split_docs(s)
    out = []
    for header, body in docs:
        fid = re.search(r'&(-?\d+)', header).group(1)
        if fid in RT:
            for key, val in RT[fid].items():
                pat = re.compile(r'(\n  ' + key + r': )[^\n]*')
                assert pat.search(body), (fid, key)
                body = pat.sub(lambda m: m.group(1) + val, body, count=1)
        if fid in FONTS:
            for key in ("m_FontSize", "m_MaxSize"):
                pat = re.compile(r'(\n    ' + key + r': )\d+')
                assert pat.search(body), (fid, key)
                body = pat.sub(lambda m: m.group(1) + str(FONTS[fid]), body, count=1)
        out.append(header + body)
    io.open(PREFAB, "w", encoding="utf-8", newline="\n").write(head + "".join(out))
    print("prefab geometry patched")


# ---------- 场景实例：清掉把面板拉歪的覆盖 ----------
SCENES = ["Assets/_Scenes/Home.unity", "Assets/_Scenes/Map.unity"]
DROP = {
    "191865702693248147": None,   # text1 的 scale / pos
    "2072494826346800501": None,  # text2 的 scale / pos
    "2355152399712804049": ["m_Sprite"],  # ima2 被清空的图，恢复
    "4720292601761052969": ["m_AnchorMax.y", "m_AnchorMin.y", "m_SizeDelta.x",
                            "m_SizeDelta.y", "m_AnchoredPosition.x", "m_AnchoredPosition.y"],
    "6085170033539385558": ["m_AnchoredPosition.y"],
    "9122441691256389096": ["m_SizeDelta.x", "m_SizeDelta.y", "m_AnchoredPosition.x",
                            "m_AnchoredPosition.y"],
}
ROOT = "8793823573447025109"
ROOT_DROP = ["m_Pivot.x", "m_Pivot.y", "m_AnchorMax.x", "m_AnchorMax.y", "m_AnchorMin.x",
             "m_AnchorMin.y", "m_SizeDelta.x", "m_SizeDelta.y", "m_LocalPosition.x",
             "m_LocalPosition.y", "m_LocalPosition.z", "m_LocalRotation.w", "m_LocalRotation.x",
             "m_LocalRotation.y", "m_LocalRotation.z", "m_AnchoredPosition.x",
             "m_AnchoredPosition.y", "m_LocalEulerAnglesHint.x", "m_LocalEulerAnglesHint.y",
             "m_LocalEulerAnglesHint.z"]


def strip_scene(path):
    s = io.open(path, encoding="utf-8").read()
    i = s.find("guid: 45c5541ea8cbd194f8138524693fa094")
    if i < 0:
        print(path, "no instance"); return
    # 定位该 PrefabInstance 文档
    start = s.rfind("--- !u!1001 &", 0, i)
    end = s.find("\n--- ", i)
    blk = s[start:end]
    mods_start = blk.index("    m_Modifications:\n")
    mods_end = blk.index("    m_RemovedComponents:")
    head = blk[:mods_start] + "    m_Modifications:\n"
    tail = blk[mods_end:]
    body = blk[mods_start + len("    m_Modifications:\n"):mods_end]

    pat = re.compile(
        r'    - target: \{fileID: (-?\d+), guid: 45c5541ea8cbd194f8138524693fa094,\n'
        r'        type: 3\}\n'
        r'      propertyPath: ([^\n]+)\n'
        r'      value: [^\n]*\n'
        r'      objectReference: \{fileID: \d+\}\n')
    kept, removed = [], 0
    for m in pat.finditer(body):
        fid, prop = m.group(1), m.group(2)
        drop = False
        if fid == ROOT and prop in ROOT_DROP:
            drop = True
        elif fid in DROP:
            lst = DROP[fid]
            if lst is None or prop in lst:
                drop = True
        if drop:
            removed += 1
        else:
            kept.append(m.group(0))
    new = s[:start] + head + "".join(kept) + tail + s[end:]
    io.open(path, "w", encoding="utf-8", newline="\n").write(new)
    print(path, "removed overrides:", removed, "kept:", len(kept))


if __name__ == "__main__":
    patch_prefab()
    for p in SCENES:
        strip_scene(p)
