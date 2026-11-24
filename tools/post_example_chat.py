import sys, math
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from style_ad import (rings, brackets, chat_icon, gradient, text_img, rounded, place, NAVY, DNAVY, BLUE, CYAN, PURPLE,
                      WHITE, GRAY, AR, EN, EN_SB)

W, H = 1080, 1350
f = Image.new("RGBA", (W, H), NAVY + (255,))
# glow + rings
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((90, 380, 990, 1280), fill=255)
glow = glow.filter(ImageFilter.GaussianBlur(200)).point(lambda v: int(v * 0.45))
f.paste(Image.new("RGBA", (W, H), DNAVY + (255,)), (0, 0), glow)
tint = Image.new("L", (W, H), 0); ImageDraw.Draw(tint).ellipse((240, 520, 840, 1120), fill=255)
tint = tint.filter(ImageFilter.GaussianBlur(160)).point(lambda v: int(v * 0.16))
f.paste(Image.new("RGBA", (W, H), BLUE + (255,)), (0, 0), tint)
r = rings().resize((1300, 1300), Image.LANCZOS)
f.alpha_composite(r, (W // 2 - 650, 830 - 650))

def ov():
    l = Image.new("RGBA", f.size, (0, 0, 0, 0)); return l, ImageDraw.Draw(l)

# top bar: logo + handle
place(f, text_img("NEXO", EN, 70, WHITE, rtl=False), 150, 95)
place(f, text_img("nexodeveloper", EN_SB, 34, GRAY, rtl=False), W - 190, 95)
l, d = ov(); d.line((80, 150, W - 80, 150), fill=(169, 184, 204, 40), width=2); f.alpha_composite(l)

# headline
place(f, text_img("محلك يبيع", AR, 112, WHITE), W / 2, 255)
place(f, text_img("حتى وإنت نايم", AR, 112, CYAN, glow=12), W / 2, 385)
place(f, text_img("موظف مبيعات ذكي يرد بثانية + موقع احترافي لمحلك", AR, 38, GRAY), W / 2, 478)

# phone mockup
PX, PY, PW, PH = W // 2, 840, 620, 560
ph = rounded(PW, PH, 64, DNAVY, border=(0, 212, 255, 150))
place(f, ph, PX, PY)
top = PY - PH // 2
# status: moon + 2:00 AM
l, d = ov()
mx, my = PX - 180, top + 52
d.ellipse((mx - 22, my - 22, mx + 22, my + 22), fill=WHITE + (235,))
d.ellipse((mx - 10, my - 30, mx + 30, my + 12), fill=DNAVY + (255,))
f.alpha_composite(l)
place(f, text_img("2:00 AM", EN_SB, 36, GRAY, rtl=False), PX + 160, top + 52)

def gray_b(txt, s=34):
    tx = text_img(txt, AR, s, (220, 226, 234))
    b = rounded(tx.width - 80 + 56, s + 44, (s + 44) // 2, (18, 30, 52), border=(169, 184, 204, 110), shadow=False).copy()
    b.alpha_composite(tx, ((b.width - tx.width) // 2, (b.height - tx.height) // 2)); return b
def bot_b(txt, s=34):
    tx = text_img(txt, AR, s, WHITE)
    b = rounded(tx.width - 80 + 56, s + 44, (s + 44) // 2, BLUE, grad=(BLUE, (0, 150, 255)), shadow=False).copy()
    b.alpha_composite(tx, ((b.width - tx.width) // 2, (b.height - tx.height) // 2)); return b

y = top + 130
b = gray_b("مرحبا، متوفر؟ شكد السعر؟", 30)
place(f, b, PX - PW / 2 + 30 + b.width / 2 - 40, y)
t = text_img("00:01", EN, 34, CYAN, rtl=False)
tc = rounded(t.width - 80 + 40, 64, 32, NAVY, border=(0, 212, 255, 220), shadow=False).copy()
tc.alpha_composite(t, ((tc.width - t.width) // 2, (tc.height - t.height) // 2))
place(f, tc, PX + PW / 2 - 30 - tc.width / 2 + 40, y + 85)
b = bot_b("هلا بيك! متوفر، وهذي التفاصيل", 30)
place(f, b, PX + PW / 2 - 30 - b.width / 2 + 40, y + 170)
# product mini cards
for k in range(3):
    card = rounded(130, 120, 22, DNAVY, border=(0, 212, 255, 150), shadow=False).copy()
    g = gradient(104, 64, *[(BLUE, CYAN), (BLUE, PURPLE), (CYAN, PURPLE)][k]).convert("RGBA")
    m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 104, 64), 14, fill=255)
    card.paste(g, (53, 53), m)
    ImageDraw.Draw(card).rounded_rectangle((58, 128, 125, 140), 6, fill=(169, 184, 204, 120))
    place(f, card, PX + 160 - k * 160, y + 270)
b = bot_b("تم تثبيت طلبك ✓", 34)
place(f, b, PX, y + 392)
brackets(f, PX, PY, 640, 0, 5.0)

# side chips
def chip(txt):
    tx = text_img(txt, AR, 34, WHITE)
    c = rounded(tx.width - 80 + 60, 78, 39, (7, 19, 38), border=(0, 212, 255, 200), shadow=False).copy()
    c.alpha_composite(tx, ((c.width - tx.width) // 2, (c.height - tx.height) // 2)); return c
place(f, chip("ماسنجر · إنستا · واتساب"), W / 2, 1185)

# bottom CTA bar
l, d = ov(); d.rectangle((0, 1230, W, H), fill=(4, 9, 22, 235)); d.line((0, 1230, W, 1230), fill=CYAN + (120,), width=3); f.alpha_composite(l)
btn = rounded(330, 84, 42, BLUE, grad=(BLUE, (0, 160, 255)), shadow=False).copy()
bt = text_img("راسلنا هسه", AR, 40, WHITE); btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
place(f, btn, W - 230, 1290)
place(f, text_img("nexodeveloper.net", EN_SB, 34, GRAY, rtl=False), 230, 1290)

f.convert("RGB").save("nexo-post.jpg", quality=93)
print("ok")
