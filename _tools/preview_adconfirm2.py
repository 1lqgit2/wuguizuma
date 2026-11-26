"""按主 Canvas 参考分辨率预览 AdConfirm（16:9 与 20:9 两种画布宽度）。"""
from PIL import Image, ImageDraw, ImageFont

R = r"C:\Unity\project\Unity2022_乌龟祖码\Assets\AdSDK\Resources"
FONT = r"C:\Unity\project\Unity2022_乌龟祖码\Assets\AdSDK\Font\DroidSansFallback.ttf"

PANEL = (480, 436)
TITLE = "添加金币"
BODY = "看广告获得奖励"


def render(W, H, out):
    CX, CY = W // 2, H // 2
    base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(126 - 46 * t), int(180 - 34 * t), int(96 + 22 * t), 255))
    d.text((CX, int(H * 0.26)), "游戏主界面（示意）", font=ImageFont.truetype(FONT, 44),
           fill=(255, 255, 255, 160), anchor="mm")

    img = Image.alpha_composite(base, Image.new("RGBA", (W, H), (0, 0, 0, 180)))
    pw, ph = PANEL
    px, py = CX - pw // 2, CY - ph // 2
    img.alpha_composite(Image.open(R + r"\侧边栏底板.png").convert("RGBA").resize((pw, ph), Image.LANCZOS), (px, py))

    def u2p(x, y):
        return px + pw / 2 + x, py + ph / 2 - y

    def put(sprite, size, center):
        im = Image.open(R + "\\" + sprite).convert("RGBA").resize(
            (int(size[0]), int(size[1])), Image.LANCZOS)
        img.alpha_composite(im, (int(center[0] - size[0] / 2), int(center[1] - size[1] / 2)))

    put("按钮.png", (250, 86), u2p(0, -68))
    put("领取按钮.png", (220, 49), u2p(0, -148))

    d = ImageDraw.Draw(img)
    d.text(u2p(0, 182), TITLE, font=ImageFont.truetype(FONT, 50), fill=(0, 0, 0, 255), anchor="mm")
    d.text(u2p(0, 30), BODY, font=ImageFont.truetype(FONT, 50), fill=(0, 0, 0, 255), anchor="mm")
    d.text(u2p(0, -68), "确认", font=ImageFont.truetype(FONT, 40), fill=(255, 255, 255, 255), anchor="mm")
    d.text(u2p(0, -148), "返回", font=ImageFont.truetype(FONT, 32), fill=(255, 255, 255, 255), anchor="mm")
    img.convert("RGB").save(out)
    return out


a = render(640, 1136, r"C:\Unity\project\_adconfirm_169.png")
b = render(565, 1255, r"C:\Unity\project\_adconfirm_209.png")

A, B = Image.open(a), Image.open(b)
H = 900
A = A.resize((int(A.width * H / A.height), H), Image.LANCZOS)
B = B.resize((int(B.width * H / B.height), H), Image.LANCZOS)
canvas = Image.new("RGB", (A.width + B.width + 30, H), (28, 28, 32))
canvas.paste(A, (0, 0))
canvas.paste(B, (A.width + 30, 0))
canvas.save(r"C:\Unity\project\_adconfirm_preview.png")
print("saved", canvas.size)
