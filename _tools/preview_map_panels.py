# -*- coding: utf-8 -*-
"""预览 Map 场景里两个弹窗在 16:9 / 20:9 主画布下的实际大小与位置。
Map 主 Canvas: 640x1136, Screen Space - Camera, match 0.5"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

R = "Assets/AdSDK/Resources/"
FONT = "Assets/AdSDK/Font/DroidSansFallback.ttf"
SS = 2  # 超采样


def sprite(name, w, h):
    im = Image.open(R + name).convert("RGBA")
    return im.resize((max(1, int(w * SS)), max(1, int(h * SS))), Image.LANCZOS)


def base_canvas(W, H):
    """模拟 Map 关卡选关界面底色 + 半透明黑遮罩"""
    W, H = W * SS, H * SS
    yy = np.linspace(0, 1, H)[:, None]
    base = np.zeros((H, W, 3), np.uint8)
    base[..., 0] = (120 - 30 * yy).astype(np.uint8)
    base[..., 1] = (170 - 40 * yy).astype(np.uint8)
    base[..., 2] = (120 + 10 * yy).astype(np.uint8)
    img = Image.fromarray(base).convert("RGBA")
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 170)))
    return img


def render_cebian(W, H):
    img = base_canvas(W, H)
    cx, cy = W * SS / 2, H * SS / 2
    bw, bh = 520 * SS, 480 * SS
    img.alpha_composite(sprite("侧边栏底板.png", 520, 480), (int(cx - bw / 2), int(cy - bh / 2)))

    def px(u, v):
        return cx + u * SS, cy - v * SS

    f = lambda n: ImageFont.truetype(FONT, int(n * SS))
    d = ImageDraw.Draw(img)
    d.text(px(0, 202), "侧边栏", font=f(40), fill=(50, 50, 50), anchor="mm")
    cl = sprite("close (2).png", 64, 66)
    x, y = px(228, 200)
    img.alpha_composite(cl, (int(x - 32 * SS), int(y - 33 * SS)))
    d.text((px(-220, 155)[0], px(0, 155)[1]), "1，点击抖音主界面侧边栏图标",
           font=f(26), fill=(50, 50, 50), anchor="lm")
    x, y = px(0, 81)
    img.alpha_composite(sprite("ima1.png", 270, 97), (int(x - 135 * SS), int(y - 48.5 * SS)))
    d.text((px(-220, 0)[0], px(0, 0)[1]), "2，点击同款小游戏进入",
           font=f(26), fill=(50, 50, 50), anchor="lm")
    x, y = px(0, -73)
    img.alpha_composite(sprite("ima2.png", 270, 95), (int(x - 135 * SS), int(y - 47.5 * SS)))
    x, y = px(0, -178)
    img.alpha_composite(sprite("按钮.png", 280, 97), (int(x - 140 * SS), int(y - 48.5 * SS)))
    d.text((x, y), "前往侧边栏", font=f(26), fill=(50, 50, 50), anchor="mm")
    return img.convert("RGB")


def render_adconfirm(W, H):
    img = base_canvas(W, H)
    cx, cy = W * SS / 2, H * SS / 2
    pw, ph = 480, 436
    img.alpha_composite(sprite("侧边栏底板.png", pw, ph),
                        (int(cx - pw * SS / 2), int(cy - ph * SS / 2)))

    def px(u, v):
        return cx + u * SS, cy - v * SS

    f = lambda n: ImageFont.truetype(FONT, int(n * SS))
    d = ImageDraw.Draw(img)
    d.text(px(0, 182), "添加金币", font=f(50), fill=(0, 0, 0), anchor="mm")
    d.text(px(0, 30), "看广告获得奖励", font=f(50), fill=(0, 0, 0), anchor="mm")
    x, y = px(0, -68)
    img.alpha_composite(sprite("按钮.png", 250, 86), (int(x - 125 * SS), int(y - 43 * SS)))
    d.text((x, y), "确认", font=f(40), fill=(255, 255, 255), anchor="mm")
    x, y = px(0, -148)
    img.alpha_composite(sprite("领取按钮.png", 220, 49), (int(x - 110 * SS), int(y - 24.5 * SS)))
    d.text((x, y), "返回", font=f(32), fill=(255, 255, 255), anchor="mm")
    return img.convert("RGB")


def canvas_size(ratio_name):
    # 主 Canvas 640x1136 中间适配：16:9 -> 640x1136；20:9 -> 约 565x1256
    return (640, 1136) if ratio_name == "16:9" else (565, 1256)


TH = 620          # 每格画布高度
TITLE_H = 56      # 每格标题高度
gap = 26
rows = []
for panel_name, fn in (("cebianPanel", render_cebian), ("AdConfirm", render_adconfirm)):
    row = []
    for ratio in ("16:9", "20:9"):
        W, H = canvas_size(ratio)
        im = fn(W, H)
        w = int(im.width * TH / im.height)
        row.append((panel_name, ratio, im.resize((w, TH), Image.LANCZOS)))
    rows.append(row)

col_w = max(c[2].width for r in rows for c in r)
row_h = TH + TITLE_H
W = col_w * 2 + gap * 3
H = row_h * 2 + gap * 3
out = Image.new("RGB", (W, H), (26, 26, 30))
d = ImageDraw.Draw(out)
fnt = ImageFont.truetype(FONT, 24)
for ri, row in enumerate(rows):
    for ci, (name, ratio, im) in enumerate(row):
        x = gap + ci * (col_w + gap) + (col_w - im.width) // 2
        y = gap + ri * (row_h + gap)
        out.paste(im, (x, y + TITLE_H))
        cw, ch = canvas_size(ratio)
        d.text((x + im.width // 2, y + 4), "%s · %s" % (name, ratio),
               font=fnt, fill=(235, 235, 240), anchor="mt")
        d.text((x + im.width // 2, y + 26), "主画布 %d×%d" % (cw, ch),
               font=ImageFont.truetype(FONT, 19), fill=(160, 162, 170), anchor="mt")
out.save("C:/Unity/project/_map_panels_preview.png")
print("saved", out.size)
