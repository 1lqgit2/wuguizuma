# -*- coding: utf-8 -*-
"""从备份恢复后，擦除旧标题并重绘两行新游戏名。"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import shutil, os

ROOT = r"C:\Unity\project\Unity2022_乌龟祖码\Assets\Sprites"
SRC = r"C:\Unity\project\_backup_i18n_20261123_1825\name2_甜趣闯关消消.png"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

p = ROOT + r"\name2.png"
shutil.copyfile(SRC, p)

im = Image.open(p).convert("RGBA")
a = np.array(im).astype(np.float32)

X0, X1 = 62, 440
Y0, Y1 = 104, 302

TOP = a[Y0 - 9:Y0 - 3, X0:X1, :3].mean(axis=0)
BOT = a[Y1 + 3:Y1 + 9, X0:X1, :3].mean(axis=0)

h = Y1 - Y0
t = np.linspace(0, 1, h)[:, None, None]
fill = TOP[None, :, :] * (1 - t) + BOT[None, :, :] * t
a[Y0:Y1, X0:X1, :3] = fill

# 擦除后做一次轻微纵向保纹平滑，防止接缝
im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")

SIZE = 70
font = ImageFont.truetype(BOLD, SIZE, index=0)
LINES = ["指尖消彩", "万物焕新"]
CY = [162, 242]

shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
ld = ImageDraw.Draw(layer)

cx = 250
for text, cy in zip(LINES, CY):
    bb = font.getbbox(text)
    w, hh = bb[2] - bb[0], bb[3] - bb[1]
    pos = (cx - w / 2 - bb[0], cy - hh / 2 - bb[1])
    sd.text((pos[0] + 2, pos[1] + 8), text, font=font,
            fill=(60, 36, 18, 145), stroke_width=6, stroke_fill=(60, 36, 18, 145))
    ld.text(pos, text, font=font, fill=(255, 255, 255, 255),
            stroke_width=5, stroke_fill=(104, 66, 38, 255))
    print(text, "bbox", bb, "pos", pos)

shadow = shadow.filter(ImageFilter.GaussianBlur(7))
im = Image.alpha_composite(im, shadow)
im = Image.alpha_composite(im, layer)
im.save(p)
print("saved")
