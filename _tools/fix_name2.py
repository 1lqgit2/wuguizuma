"""用列向插值擦除 name2.png 旧文字，保留竖直木纹，再写中文标题。"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"C:\Unity\project\Unity2022_乌龟祖码\Assets\Sprites"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

p = ROOT + r"\name2.png"
im = Image.open(p).convert("RGBA")
a = np.array(im).astype(np.float32)

X0, X1 = 66, 436      # 擦除区左右
Y0, Y1 = 114, 304     # 擦除区上下
TOP = a[Y0 - 8:Y0 - 2, X0:X1, :3].mean(axis=0)     # 上方干净木纹
BOT = a[Y1 + 2:Y1 + 8, X0:X1, :3].mean(axis=0)     # 下方干净木纹

h = Y1 - Y0
t = np.linspace(0, 1, h)[:, None, None]
fill = TOP[None, :, :] * (1 - t) + BOT[None, :, :] * t
# 轻微压缩动态范围，避免接缝生硬
a[Y0:Y1, X0:X1, :3] = fill

im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def fit_font(text, max_w, start=90, path=BOLD):
    size = start
    while size > 12:
        f = ImageFont.truetype(path, size, index=0)
        b = f.getbbox(text)
        if b[2] - b[0] <= max_w:
            return f, size
        size -= 2
    return ImageFont.truetype(path, 12, index=0), 12


text = "甜趣闯关消消"
font, size = fit_font(text, 336, start=66)
print("font", size)

bbox = font.getbbox(text)
w, hh = bbox[2] - bbox[0], bbox[3] - bbox[1]
cx, cy = 250, 232
pos = (cx - w / 2 - bbox[0], cy - hh / 2 - bbox[1])

shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
ImageDraw.Draw(shadow).text((pos[0] + 2, pos[1] + 10), text, font=font,
                            fill=(62, 38, 20, 140), stroke_width=6,
                            stroke_fill=(62, 38, 20, 140))
shadow = shadow.filter(ImageFilter.GaussianBlur(8))
im = Image.alpha_composite(im, shadow)

layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
d.text(pos, text, font=font, fill=(255, 255, 255, 255), stroke_width=5,
       stroke_fill=(104, 66, 38, 255))
# 顶部高光
hi = Image.new("RGBA", im.size, (0, 0, 0, 0))
ImageDraw.Draw(hi).text((pos[0], pos[1] - 2), text, font=font,
                        fill=(255, 255, 255, 0), stroke_width=0)
im = Image.alpha_composite(im, layer)
im.save(p)
print("saved")
