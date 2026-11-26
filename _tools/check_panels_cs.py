# -*- coding: utf-8 -*-
import io, re

files = (
    "Assets/AdSDK/Scripts/AdConfirm.cs",
    "Assets/AdSDK/Scripts/cebian.cs",
    "Assets/AdSDK/Scripts/PopupLayer.cs",
    "Assets/AdSDK/Scripts/PanelLauncher.cs",
)

for f in files:
    s = io.open(f, encoding="utf-8").read()
    t = re.sub(r"//[^\n]*", "", s)
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', t)
    ok = t.count("{") == t.count("}") and t.count("(") == t.count(")")
    print(f, "braces", t.count("{"), t.count("}"),
          "parens", t.count("("), t.count(")"),
          "lines", len(s.splitlines()), "OK" if ok else "!! MISMATCH")

# 关键符号检查
ac = io.open(files[0], encoding="utf-8").read()
cb = io.open(files[1], encoding="utf-8").read()
print("AdConfirm.OpenFromButton:", "public static void OpenFromButton" in ac)
print("AdConfirm.PopupLayer 使用:", "PopupLayer.Get()" in ac)
print("cebian.OpenPanel:", "public static void OpenPanel" in cb)
print("cebian.PopupLayer 使用:", "PopupLayer.Get()" in cb)
