"""重绘 logo-shophia-ng.png 与 name2.png 上的文字为中文。"""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"C:\Unity\project\Unity2022_乌龟祖码\Assets\Sprites"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def fit_font(text, max_w, start=120, path=BOLD):
    size = start
    while size > 12:
        f = ImageFont.truetype(path, size, index=0)
        w = f.getbbox(text)[2] - f.getbbox(text)[0]
        if w <= max_w:
            return f, size, w
        size -= 2
    return ImageFont.truetype(path, 12, index=0), 12, 0


def styled_text(base, center, text, font, fill=(255, 255, 255),
                stroke=(96, 62, 36), stroke_w=5, shadow=(58, 36, 20),
                shadow_alpha=150, blur=7, offset=(0, 9)):
    """在 base(RGBA) 上绘制带描边 + 投影的文字，返回新图层。"""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    pos = (center[0] - w / 2 - bbox[0], center[1] - h / 2 - bbox[1])

    # 投影
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.text((pos[0] + offset[0], pos[1] + offset[1]), text, font=font,
           fill=shadow + (shadow_alpha,), stroke_width=stroke_w,
           stroke_fill=shadow + (shadow_alpha,))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.alpha_composite(layer, sh)

    d = ImageDraw.Draw(layer)
    d.text(pos, text, font=font, fill=fill + (255,),
           stroke_width=stroke_w, stroke_fill=stroke + (255,))
    return Image.alpha_composite(base, layer)


# ---------------- 1. logo-shophia-ng.png ----------------
def do_logo():
    p = ROOT + r"\logo-shophia-ng.png"
    im = Image.open(p).convert("RGBA")
    a = np.array(im)
    gray = a[:, :, :3].mean(axis=2)
    ys, xs = np.where(gray > 45)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    print("logo text bbox", x0, y0, x1, y1)

    # 用干净黑底覆盖原文字区域
    bg = tuple(int(v) for v in a[y0 - 20, max(x0 - 40, 0)][:3])
    d = ImageDraw.Draw(im)
    d.rectangle([x0 - 18, y0 - 18, x1 + 18, y1 + 18], fill=bg + (255,))

    text = "尼奥游戏"
    font, size, w = fit_font(text, x1 - x0 + 30, start=170)
    print("logo font", size, "width", w)

    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bbox = font.getbbox(text)
    pos = ((im.size[0] - (bbox[2] - bbox[0])) / 2 - bbox[0],
           (y0 + y1) / 2 - (bbox[3] - bbox[1]) / 2 - bbox[1])
    ImageDraw.Draw(layer).text(pos, text, font=font, fill=(255, 255, 255, 255))
    # 轻微发光，贴近原图柔边
    glow = layer.filter(ImageFilter.GaussianBlur(6))
    glow.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.55)))
    im = Image.alpha_composite(im, glow)
    im = Image.alpha_composite(im, layer)
    im.save(p)
    print("saved", p)


# ---------------- 2. name2.png ----------------
def do_name2():
    p = ROOT + r"\name2.png"
    im = Image.open(p).convert("RGBA")
    a = np.array(im)

    # 文字区域（木牌内部）
    ry0, ry1, rx0, rx1 = 108, 302, 70, 432
    sub = a[ry0:ry1, rx0:rx1, :3].astype(np.int16)
    mn = sub.min(axis=2)
    mean = sub.mean(axis=2)
    mask = ((mn > 238) | (mean < 180)).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=1)

    full = np.zeros(a.shape[:2], np.uint8)
    full[ry0:ry1, rx0:rx1] = mask
    bgr = cv2.cvtColor(a[:, :, :3], cv2.COLOR_RGB2BGR)
    inp = cv2.inpaint(bgr, full, 7, cv2.INPAINT_TELEA)
    im = Image.fromarray(cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)).convert("RGBA")
    im.putalpha(Image.fromarray(a[:, :, 3]))

    text = "甜趣闯关消消"
    font, size, w = fit_font(text, 352, start=70)
    print("name2 font", size, "width", w)
    im = styled_text(im, (250, 205), text, font, stroke_w=5,
                     shadow_alpha=140, blur=8, offset=(0, 9))
    im.save(p)
    print("saved", p)


if __name__ == "__main__":
    do_logo()
    do_name2()
