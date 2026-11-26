# -*- coding: utf-8 -*-
import io
import re

files = [
    "Assets/AdSDK/Scripts/AdConfirm.cs",
    "Assets/AdSDK/Scripts/AdManager.cs",
    "Assets/AdSDK/Scripts/TikTokPlatform.cs",
    "Assets/Scripts/CUtils.cs",
    "Assets/Scripts/PauseDialog.cs",
    "Assets/Scripts/RewardedButton.cs",
]

for f in files:
    s = io.open(f, encoding="utf-8").read()
    t = s
    # 去掉行注释
    t = "\n".join(line.split("//")[0] if '"' not in line else line for line in t.split("\n"))
    # 去掉块注释
    t = re.sub(r"/\*[\s\S]*?\*/", "", t)
    # 去掉字符串
    t = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', t)
    t = re.sub(r"'(?:[^'\\\n]|\\.)*'", "''", t)
    print(f, "braces", t.count("{"), t.count("}"),
          "OK" if t.count("{") == t.count("}") else "MISMATCH",
          "parens", t.count("("), t.count(")"),
          "OK" if t.count("(") == t.count(")") else "MISMATCH")

p = io.open("Assets/AdSDK/Resources/AdConfirm.prefab", encoding="utf-8").read()
print("AdConfirm defaultReward:", "defaultRewardAmount: 50" in p)

q = io.open("Assets/Prefab/ShopDialog.prefab", encoding="utf-8").read()
print("Shop rewardAmount:", "rewardAmount: 50" in q)
ids = re.findall(r"(?m)^--- !u!\d+ &(-?\d+)", q)
print("ShopDialog docs:", len(ids), "dup:", [x for x in set(ids) if ids.count(x) > 1])
