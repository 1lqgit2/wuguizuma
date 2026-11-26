# -*- coding: utf-8 -*-
"""给 ShopDialog 的 RewardedVideo 节点补上 Image + Button + 文字，
让它真正可点击（原来只有 RectTransform 和脚本，玩家点不到，激励奖励拿不到）。
"""
import io, re

P = "Assets/Prefab/ShopDialog.prefab"
s = io.open(P, encoding="utf-8").read()

RT_VIDEO = "1790492667549791008"
GO_VIDEO = "1790492663808471559"
RT_ICON = "1790492667549791005"
GO_ICON = "1790492663808471601"
SCRIPT_REWARDED = "1790492665704297520"

CR = "8100000000000000001"
IMG = "8100000000000000002"
BTN = "8100000000000000003"
CR2 = "8100000000000000004"
TXT = "8100000000000000005"

for fid in (CR, IMG, BTN, CR2, TXT):
    assert ("&%s\n" % fid) not in s, "fileID 冲突: " + fid

# ---------- 1) RewardedVideo 的组件列表 ----------
old_comp = """  m_Component:
  - component: {fileID: 1790492667549791008}
  - component: {fileID: 1790492665704297520}"""
new_comp = """  m_Component:
  - component: {fileID: 1790492667549791008}
  - component: {fileID: %s}
  - component: {fileID: %s}
  - component: {fileID: %s}
  - component: {fileID: 1790492665704297520}""" % (CR, IMG, BTN)
assert s.count(old_comp) == 1, s.count(old_comp)
s = s.replace(old_comp, new_comp, 1)

# ---------- 2) Content 的组件列表 ----------
old_comp2 = """  m_Component:
  - component: {fileID: 1790492667549791005}"""
new_comp2 = """  m_Component:
  - component: {fileID: 1790492667549791005}
  - component: {fileID: %s}
  - component: {fileID: %s}""" % (CR2, TXT)
assert s.count(old_comp2) == 1, s.count(old_comp2)
s = s.replace(old_comp2, new_comp2, 1)

# ---------- 3) 追加组件文档 ----------
docs = """
--- !u!222 &{cr}
CanvasRenderer:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_video}}}
  m_CullTransparentMesh: 0
--- !u!114 &{img}
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_video}}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: -765806418, guid: f70555f144d8491a825f0804e09c671c, type: 3}}
  m_Name: 
  m_EditorClassIdentifier: 
  m_Material: {{fileID: 0}}
  m_Color: {{r: 1, g: 1, b: 1, a: 1}}
  m_RaycastTarget: 1
  m_OnCullStateChanged:
    m_PersistentCalls:
      m_Calls: []
  m_Sprite: {{fileID: 21300030, guid: 0f8d3ebf70b6434e80de4fccda57fd6a, type: 3}}
  m_Type: 0
  m_PreserveAspect: 1
  m_FillCenter: 1
  m_FillMethod: 4
  m_FillAmount: 1
  m_FillClockwise: 1
  m_FillOrigin: 0
  m_UseSpriteMesh: 0
--- !u!114 &{btn}
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_video}}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 1392445389, guid: f70555f144d8491a825f0804e09c671c, type: 3}}
  m_Name: 
  m_EditorClassIdentifier: 
  m_Navigation:
    m_Mode: 3
    m_SelectOnUp: {{fileID: 0}}
    m_SelectOnDown: {{fileID: 0}}
    m_SelectOnLeft: {{fileID: 0}}
    m_SelectOnRight: {{fileID: 0}}
  m_Transition: 1
  m_Colors:
    m_NormalColor: {{r: 1, g: 1, b: 1, a: 1}}
    m_HighlightedColor: {{r: 0.9607843, g: 0.9607843, b: 0.9607843, a: 1}}
    m_PressedColor: {{r: 0.7843137, g: 0.7843137, b: 0.7843137, a: 1}}
    m_DisabledColor: {{r: 0.7843137, g: 0.7843137, b: 0.7843137, a: 0.5019608}}
    m_ColorMultiplier: 1
    m_FadeDuration: 0.1
  m_SpriteState:
    m_HighlightedSprite: {{fileID: 0}}
    m_PressedSprite: {{fileID: 0}}
    m_DisabledSprite: {{fileID: 0}}
  m_AnimationTriggers:
    m_NormalTrigger: Normal
    m_HighlightedTrigger: Highlighted
    m_PressedTrigger: Pressed
    m_DisabledTrigger: Disabled
  m_Interactable: 1
  m_TargetGraphic: {{fileID: {img}}}
  m_OnClick:
    m_PersistentCalls:
      m_Calls:
      - m_Target: {{fileID: {script}}}
        m_TargetAssemblyTypeName: RewardedButton, Assembly-CSharp
        m_MethodName: OnClick
        m_Mode: 1
        m_Arguments:
          m_ObjectArgument: {{fileID: 0}}
          m_ObjectArgumentAssemblyTypeName: UnityEngine.Object, UnityEngine
          m_IntArgument: 0
          m_FloatArgument: 0
          m_StringArgument: 
          m_BoolArgument: 0
        m_CallState: 2
--- !u!222 &{cr2}
CanvasRenderer:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_icon}}}
  m_CullTransparentMesh: 0
--- !u!114 &{txt}
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_icon}}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 708705254, guid: f70555f144d8491a825f0804e09c671c, type: 3}}
  m_Name: 
  m_EditorClassIdentifier: 
  m_Material: {{fileID: 0}}
  m_Color: {{r: 1, g: 1, b: 1, a: 1}}
  m_RaycastTarget: 0
  m_OnCullStateChanged:
    m_PersistentCalls:
      m_Calls: []
  m_FontData:
    m_Font: {{fileID: 12800000, guid: 4b55cb2df6c16834786823b918fe5b7f, type: 3}}
    m_FontSize: 26
    m_FontStyle: 1
    m_BestFit: 1
    m_MinSize: 14
    m_MaxSize: 26
    m_Alignment: 4
    m_AlignByGeometry: 0
    m_RichText: 1
    m_HorizontalOverflow: 0
    m_VerticalOverflow: 1
    m_LineSpacing: 1
  m_Text: "\\u770B\\u5E7F\\u544A"
""".format(cr=CR, img=IMG, btn=BTN, cr2=CR2, txt=TXT,
           go_video=GO_VIDEO, go_icon=GO_ICON, script=SCRIPT_REWARDED)

# 保证文件以换行结尾后追加
if not s.endswith("\n"):
    s += "\n"
s += docs

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched")

# ---------- 校验 ----------
t = io.open(P, encoding="utf-8").read()
ids = re.findall(r'(?m)^--- !u!\d+ &(-?\d+)', t)
dup = [x for x in set(ids) if ids.count(x) > 1]
print("docs:", len(ids), "dup:", dup)
refs = set(re.findall(r'fileID: (-?\d+)', t)) - {"0"}
missing = sorted(r for r in refs if r not in ids and not r.startswith("1280000") and r != "-765806418")
print("missing refs:", missing[:10])
print("adText:", "\\u770B\\u5E7F\\u544A" in t)
