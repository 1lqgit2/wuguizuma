# -*- coding: utf-8 -*-
"""渲染 cebianPanel 在 16:9 / 20:9 画布下的效果预览。"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

R = "Assets/AdSDK/Resources/"
FONT = "Assets/AdSDK/Font/DroidSansFallback.ttf"
S = 1.5

def load(name, w, h):
    im = Image.open(R + name).convert("RGBA")
    return im.resize((max(1, int(w * S)), max(1, int(h * S))), Image.LANCZOS)

def render(W, H, out):
    W, H = int(W * S), int(H * S)
    # 背景：模拟游戏画面（暖色渐变 + 一点纹理感）
    yy = np.linspace(0, 1, H)[:, None]
    base = np.zeros((H, W, 3), np.uint8)
    base[..., 0] = (250 - 60 * yy).astype(np.uint8)
    base[..., 1] = (230 - 70 * yy).astype(np.uint8)
    base[..., 2] = (200 - 80 * yy).astype(np.uint8)
    img = Image.fromarray(base).convert("RGBA")
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 195)))  # 遮罩 0.76

    cx, cy = W / 2, H / 2
    bw, bh = 520 * S, 480 * S
    left, top = cx - bw / 2, cy - bh / 2

    def px(u, v):           # 面板局部坐标（中心为原点，y 向上）→ 像素
        return cx + u * S, cy - v * S

    box = load("侧边栏底板.png", 520, 480)
    img.alpha_composite(box, (int(left), int(top)))

    d = ImageDraw.Draw(img)
    fb = lambda n: ImageFont.truetype(FONT, int(n * S))

    # 标题
    d.text(px(0, 202), "侧边栏", font=fb(40), fill=(50, 50, 50), anchor="mm")
    # 关闭
    cl = load("close (2).png", 64, 66)
    x, y = px(228, 200)
    img.alpha_composite(cl, (int(x - 32 * S), int(y - 33 * S)))
    # 步骤 1
    d.text((px(-220, 155)[0], px(0, 155)[1]), "1，点击抖音主界面侧边栏图标",
           font=fb(26), fill=(50, 50, 50), anchor="lm")
    im1 = load("ima1.png", 270, 97)
    x, y = px(0, 81)
    img.alpha_composite(im1, (int(x - 135 * S), int(y - 48.5 * S)))
    # 步骤 2
    d.text((px(-220, 0)[0], px(0, 0)[1]), "2，点击同款小游戏进入",
           font=fb(26), fill=(50, 50, 50), anchor="lm")
    im2 = load("ima2.png", 270, 95)
    x, y = px(0, -73)
    img.alpha_composite(im2, (int(x - 135 * S), int(y - 47.5 * S)))
    # 前往按钮
    btn = load("按钮.png", 280, 97)
    x, y = px(0, -178)
    img.alpha_composite(btn, (int(x - 140 * S), int(y - 48.5 * S)))
    d.text((x, y), "前往侧边栏", font=fb(26), fill=(50, 50, 50), anchor="mm")

    img.convert("RGB").save(out, quality=95)
    print("saved", out, img.size)

render(640, 1136, "C:/Unity/project/_cebian_169.png")
render(565, 1256, "C:/Unity/project/_cebian_209.png")

a = Image.open("C:/Unity/project/_cebian_169.png")
b = Image.open("C:/Unity/project/_cebian_209.png")
hh = max(a.height, b.height)
canvas = Image.new("RGB", (a.width + b.width + 30, hh), (255, 255, 255))
canvas.paste(a, (0, (hh - a.height) // 2))
canvas.paste(b, (a.width + 30, (hh - b.height) // 2))
canvas.save("C:/Unity/project/_cebian_preview.png")
print("combined", canvas.size)
