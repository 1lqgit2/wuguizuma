"""修正 AdConfirm 预制体：去掉嵌套 Canvas，改成主 Canvas 下的全屏弹窗，并重排尺寸/位置。"""
import re, io

P = r"C:\Unity\project\Unity2022_乌龟祖码\Assets\AdSDK\Resources\AdConfirm.prefab"
src = io.open(P, encoding="utf-8").read()

ROOT_RT = "3639414679521888923"
ROOT_GO = "1975447345056787746"
PANEL_RT = "5940739278826569644"
TITLE_RT = "4048378648736176260"    # tips (1) 添加金币
BODY_RT = "6982292855731234361"     # tips 看广告获得奖励
BTN_OK_RT = "5986475748416804390"   # btn_confirm 确认
BTN_BACK_RT = "3069782753904627285"  # btn_close 返回
REMOVE = {"1227633364860318004": "223",   # Canvas
          "4518656389285953812": "114",   # CanvasScaler
          "5463732825916665681": "114"}   # GraphicRaycaster


def block_of(fid):
    m = re.search(r'--- !u!\d+ &' + fid + r'\n', src)
    i = m.start()
    k = src.find("\n--- ", i + 10)
    return i, (k if k != -1 else len(src))


def patch_rt(fid, repl):
    global src
    i, j = block_of(fid)
    blk = src[i:j]
    for old, new in repl:
        assert old in blk, (fid, old)
        blk = blk.replace(old, new, 1)
    src = src[:i] + blk + src[j:]


# 1) 根节点全屏拉伸 + 恢复正常缩放（原来 scale 是全 0）
patch_rt(ROOT_RT, [
    ("m_AnchorMax: {x: 0, y: 0}", "m_AnchorMax: {x: 1, y: 1}"),
    ("m_Pivot: {x: 0, y: 0}", "m_Pivot: {x: 0.5, y: 0.5}"),
    ("m_LocalScale: {x: 0, y: 0, z: 0}", "m_LocalScale: {x: 1, y: 1, z: 1}"),
])

# 2) 去掉 Canvas / CanvasScaler / GraphicRaycaster（主 Canvas 已有射线检测）
i, j = block_of(ROOT_GO)
gb = src[i:j]
for cid in REMOVE:
    gb = gb.replace("  - component: {fileID: %s}\n" % cid, "", 1)
src = src[:i] + gb + src[j:]

for cid in REMOVE:
    m = re.search(r'--- !u!' + REMOVE[cid] + r' &' + cid + r'\n.*?(?=\n--- )', src, re.S)
    assert m, cid
    src = src[:m.start()] + src[m.end() + 1:]

# 3) 面板：560x508 居中（贴合底图 312x283 = 1.102 比例，原来 642x534 偏大且被锚点拉到右上角）
patch_rt(PANEL_RT, [
    ("m_AnchorMax: {x: 1, y: 1}", "m_AnchorMax: {x: 0.5, y: 0.5}"),
    ("m_SizeDelta: {x: 642.7, y: 534.7}", "m_SizeDelta: {x: 560, y: 508}"),
])

# 4) 标题条贴住顶部蓝色标签（标签高 = 508*45/283 ≈ 81）
patch_rt(TITLE_RT, [
    ("m_AnchoredPosition: {x: 0, y: -47.1698}", "m_AnchoredPosition: {x: 0, y: -42}"),
    ("m_SizeDelta: {x: 642, y: 94.3396}", "m_SizeDelta: {x: 560, y: 78}"),
])

# 5) 正文略微上移，避开按钮
patch_rt(BODY_RT, [
    ("m_AnchoredPosition: {x: 0, y: 28}", "m_AnchoredPosition: {x: 0, y: 45}"),
])

# 6) 确认按钮：贴底居中偏右，按贴图 217x75 比例（2.893）
patch_rt(BTN_OK_RT, [
    ("m_AnchoredPosition: {x: 134.9, y: 120}", "m_AnchoredPosition: {x: 140, y: 112}"),
    ("m_SizeDelta: {x: 250, y: 100}", "m_SizeDelta: {x: 230, y: 80}"),
])

# 7) 返回按钮：确认按钮左侧，按贴图 952x211 比例（4.512）
patch_rt(BTN_BACK_RT, [
    ("m_AnchoredPosition: {x: -154.7, y: 127.14}", "m_AnchoredPosition: {x: -140, y: 94.5}"),
    ("m_SizeDelta: {x: 244.1, y: 85.712}", "m_SizeDelta: {x: 220, y: 48.8}"),
])

io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("prefab patched")

# ---- 校验 ----
s2 = io.open(P, encoding="utf-8").read()
assert "1227633364860318004" not in s2 and "4518656389285953812" not in s2
for fid in (ROOT_RT, PANEL_RT, TITLE_RT, BODY_RT, BTN_OK_RT, BTN_BACK_RT):
    assert s2.count("&%s\n" % fid) == 1, fid
print("docs:", len(re.findall(r'(?m)^--- ', s2)))
