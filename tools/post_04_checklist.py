import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from render import text_img, gradient, rounded, place, NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, AR_BLACK, AR_REG, EN, EN_SB

W, H = 1080, 1350
OUT = sys.argv[1] if len(sys.argv) > 1 else "nexo-post.jpg"
f = Image.new("RGBA", (W, H), NAVY + (255,))
def ov():
    l = Image.new("RGBA", f.size, (0, 0, 0, 0)); return l, ImageDraw.Draw(l)

# diagonal gradient band behind the card
l, d = ov()
d.polygon([(0, 380), (W, 180), (W, 980), (0, 1180)], fill=BLUE + (255,))
band = Image.new("RGBA", f.size, (0, 0, 0, 0))
g = gradient(W, H, BLUE, PURPLE).convert("RGBA")
band.paste(g, (0, 0), l.split()[3])
band.putalpha(band.getchannel("A").point(lambda v: int(v * 0.55)))
f.alpha_composite(band)
l, d = ov()
for k in range(14):
    x = 60 + k * 80
    d.line((x, 0, x - 300, H), fill=WHITE + (6,), width=2)
f.alpha_composite(l)

# header
place(f, text_img("NEXO", EN, 44, WHITE, rtl=False), 115, 80)
tag = rounded(250, 62, 31, DNAVY, border=(0, 212, 255, 200), shadow=False).copy()
tt = text_img("اختبار سريع", AR, 30, CYAN); tag.alpha_composite(tt, ((tag.width - tt.width) // 2, (tag.height - tt.height) // 2))
place(f, tag, W - 170, 80)

def right(img, y, xr=W - 80):
    f.alpha_composite(img, (int(xr - img.width + 40), int(y - img.height / 2)))
right(text_img("محلك يحتاج", AR_BLACK, 92, WHITE), 205)
right(text_img("موظف مبيعات ذكي إذا…", AR_BLACK, 76, CYAN, glow=10), 310)

# white checklist card
CW, CH = 900, 720
card = Image.new("RGBA", (CW + 80, CH + 80), (0, 0, 0, 0))
sh = Image.new("L", card.size, 0); ImageDraw.Draw(sh).rounded_rectangle((40, 50, 40 + CW, 50 + CH), 48, fill=255)
card.paste(Image.new("RGBA", card.size, (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.55)))
body = Image.new("L", card.size, 0); ImageDraw.Draw(body).rounded_rectangle((40, 40, 40 + CW, 40 + CH), 48, fill=255)
card.paste(Image.new("RGBA", card.size, WHITE + (255,)), (0, 0), body)
cd = ImageDraw.Draw(card)
# clip on top
cd.rounded_rectangle((40 + CW / 2 - 110, 18, 40 + CW / 2 + 110, 74), 22, fill=DNAVY + (255,))
cd.ellipse((40 + CW / 2 - 14, 32, 40 + CW / 2 + 14, 60), fill=CYAN + (255,))
ITEMS = ["الرسائل تتراكم وما تلحك ترد عليها", "زبائن يسألون نفس الأسئلة كل يوم", "تفوتك طلبات بالليل وأيام العطل",
         "ما عندك وقت تعرض المنتجات لكل زبون", "محلك ما عنده موقع يعرّف بيه"]
for i, it in enumerate(ITEMS):
    y = 40 + 110 + i * 125
    # checkbox (right side, RTL)
    bx = 40 + CW - 80
    g2 = gradient(64, 64, BLUE, CYAN).convert("RGBA")
    m = Image.new("L", (64, 64), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 64, 64), 16, fill=255)
    card.paste(g2, (int(bx - 32), int(y - 32)), m)
    cd.line([(bx - 15, y + 1), (bx - 4, y + 13), (bx + 17, y - 12)], fill=WHITE + (255,), width=8, joint="curve")
    t = text_img(it, AR, 38, NAVY)
    card.alpha_composite(t, (int(bx - 60 - t.width + 40), int(y - t.height / 2)))
    if i < len(ITEMS) - 1:
        cd.line((40 + 70, y + 62, 40 + CW - 70, y + 62), fill=(169, 184, 204, 120), width=2)
card = card.rotate(-1.2, expand=True, resample=Image.BICUBIC)
place(f, card, W / 2, 790)

# bottom answer
right(text_img("إذا أشّرت ولو على وحدة…", AR, 44, WHITE), 1225)
btn = rounded(360, 86, 43, BLUE, grad=(BLUE, (0, 170, 255)), shadow=False).copy()
bt = text_img("راسلنا ونحلّها", AR, 38, WHITE)
btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
f.alpha_composite(btn, (70 - 40, 1225 - btn.height // 2))
place(f, text_img("بوت ذكي + موقع احترافي  ·  nexodeveloper.net", AR_REG, 24, GRAY), W / 2, 1312)

f.convert("RGB").save(OUT, quality=93)
print("ok", OUT)
