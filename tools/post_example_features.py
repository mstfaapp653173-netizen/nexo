import sys, math, random
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from style_ad import gradient, text_img, rounded, place, NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, EN, EN_SB

W, H = 1080, 1350
S = 2  # supersample for crisp lines
f = Image.new("RGBA", (W, H), NAVY + (255,))

def ov():
    l = Image.new("RGBA", f.size, (0, 0, 0, 0)); return l, ImageDraw.Draw(l)

# ---------- background: depth, bokeh, light streaks ----------
l, d = ov()
for cx, cy, r, col, a in [(200, 700, 520, BLUE, 70), (900, 300, 420, PURPLE, 45), (820, 1150, 460, CYAN, 35)]:
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (a,))
f.alpha_composite(l.filter(ImageFilter.GaussianBlur(170)))
random.seed(4)
l, d = ov()
for _ in range(38):
    x, y = random.uniform(0, W), random.uniform(0, H); r = random.uniform(3, 16)
    col = random.choice([CYAN, BLUE, (120, 200, 255)])
    d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(random.uniform(40, 120)),))
f.alpha_composite(l.filter(ImageFilter.GaussianBlur(3)))
l, d = ov()
for k, (x0, a) in enumerate([(-200, 60), (650, 40)]):
    d.polygon([(x0, 0), (x0 + 120, 0), (x0 + 520, H), (x0 + 400, H)], fill=CYAN + (a // 3,))
f.alpha_composite(l.filter(ImageFilter.GaussianBlur(40)))
# floor reflection line
l, d = ov(); d.rectangle((0, 900, W, 905), fill=CYAN + (40,)); f.alpha_composite(l.filter(ImageFilter.GaussianBlur(6)))

# ---------- glowing outline pill ----------
def glow_pill(w, h, fill=(5, 14, 32), border=CYAN, bw=3, glow=14, grad_fill=None):
    pad = 40
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + w, pad + h), h // 2, outline=255, width=bw + 4)
    g = Image.new("RGBA", im.size, border + (255,)); im.paste(g, (0, 0), m.filter(ImageFilter.GaussianBlur(glow)).point(lambda v: int(v * 0.9)))
    body = Image.new("L", im.size, 0); ImageDraw.Draw(body).rounded_rectangle((pad, pad, pad + w, pad + h), h // 2, fill=255)
    if grad_fill:
        im.paste(gradient(*im.size, *grad_fill).convert("RGBA"), (0, 0), body)
    else:
        im.paste(Image.new("RGBA", im.size, fill + (235,)), (0, 0), body)
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), h // 2, outline=border + (255,), width=bw)
    return im

def put_text_in(pill, txt, size, col=WHITE, font=AR, rtl=True, dx=0):
    tx = text_img(txt, font, size, col, rtl=rtl)
    pill.alpha_composite(tx, ((pill.width - tx.width) // 2 + dx, (pill.height - tx.height) // 2))
    return pill

# ---------- icons (cyan line icons) ----------
def icon(kind, s=56, col=CYAN):
    im = Image.new("RGBA", (s * S, s * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s * S / 2; u = s * S / 56; lw = int(5 * u)
    C = col + (255,)
    if kind == "chat":
        d.rounded_rectangle((6 * u, 8 * u, 50 * u, 40 * u), 12 * u, outline=C, width=lw)
        d.polygon([(14 * u, 38 * u), (12 * u, 50 * u), (24 * u, 40 * u)], fill=C)
        for k in range(3): d.ellipse((16 * u + k * 10 * u, 22 * u, 22 * u + k * 10 * u, 28 * u), fill=C)
    elif kind == "q":
        d.ellipse((6 * u, 6 * u, 50 * u, 50 * u), outline=C, width=lw)
        qq = text_img("؟", AR, int(30 * u), col); im.alpha_composite(qq, (int(c - qq.width / 2), int(c - qq.height / 2)))
    elif kind == "grid":
        for i in range(2):
            for j in range(2):
                d.rounded_rectangle((8 * u + i * 22 * u, 8 * u + j * 22 * u, 26 * u + i * 22 * u, 26 * u + j * 22 * u), 4 * u, outline=C, width=lw)
    elif kind == "cart":
        d.line([(4 * u, 10 * u), (14 * u, 10 * u), (20 * u, 38 * u), (46 * u, 38 * u), (51 * u, 18 * u), (16 * u, 18 * u)], fill=C, width=lw, joint="curve")
        d.ellipse((18 * u, 42 * u, 26 * u, 50 * u), fill=C); d.ellipse((38 * u, 42 * u, 46 * u, 50 * u), fill=C)
    elif kind == "clock":
        d.ellipse((6 * u, 6 * u, 50 * u, 50 * u), outline=C, width=lw)
        d.line((c, c, c, 15 * u), fill=C, width=lw); d.line((c, c, 38 * u, c + 6 * u), fill=C, width=lw)
    elif kind == "globe":
        d.ellipse((6 * u, 6 * u, 50 * u, 50 * u), outline=C, width=lw)
        d.ellipse((18 * u, 6 * u, 38 * u, 50 * u), outline=C, width=lw)
        d.line((6 * u, c, 50 * u, c), fill=C, width=lw)
    elif kind == "food":
        d.line((18 * u, 6 * u, 18 * u, 50 * u), fill=C, width=lw)
        for k in (-7, 0, 7): d.line((18 * u + k * u, 6 * u, 18 * u + k * u, 20 * u), fill=C, width=int(4 * u))
        d.ellipse((32 * u, 6 * u, 46 * u, 28 * u), outline=C, width=lw); d.line((39 * u, 28 * u, 39 * u, 50 * u), fill=C, width=lw)
    elif kind == "shirt":
        d.polygon([(18 * u, 8 * u), (6 * u, 16 * u), (12 * u, 26 * u), (16 * u, 24 * u), (16 * u, 50 * u), (40 * u, 50 * u), (40 * u, 24 * u), (44 * u, 26 * u), (50 * u, 16 * u), (38 * u, 8 * u), (34 * u, 14 * u), (22 * u, 14 * u)], outline=C, width=lw)
    elif kind == "scissors":
        d.ellipse((6 * u, 32 * u, 22 * u, 48 * u), outline=C, width=lw); d.ellipse((34 * u, 32 * u, 50 * u, 48 * u), outline=C, width=lw)
        d.line((18 * u, 34 * u, 44 * u, 6 * u), fill=C, width=lw); d.line((38 * u, 34 * u, 12 * u, 6 * u), fill=C, width=lw)
    elif kind == "bolt":
        d.polygon([(32 * u, 4 * u), (12 * u, 32 * u), (26 * u, 32 * u), (22 * u, 52 * u), (44 * u, 22 * u), (30 * u, 22 * u)], fill=C)
    elif kind == "shield":
        d.polygon([(28 * u, 4 * u), (48 * u, 12 * u), (46 * u, 32 * u), (28 * u, 52 * u), (10 * u, 32 * u), (8 * u, 12 * u)], fill=C)
        d.line([(18 * u, 28 * u), (25 * u, 35 * u), (39 * u, 20 * u)], fill=NAVY + (255,), width=lw)
    elif kind == "store":
        d.rectangle((10 * u, 24 * u, 46 * u, 50 * u), outline=C, width=lw)
        d.polygon([(6 * u, 24 * u), (12 * u, 8 * u), (44 * u, 8 * u), (50 * u, 24 * u)], outline=C, width=lw)
        d.rectangle((22 * u, 34 * u, 34 * u, 50 * u), fill=C)
    return im.resize((s, s), Image.LANCZOS)

# ---------- top brand pill ----------
bp = glow_pill(300, 78, glow=10)
put_text_in(bp, "NEXO", 52, WHITE, EN, rtl=False)
place(f, bp, W / 2, 80)

# ---------- headline pill ----------
hp = glow_pill(940, 150, glow=18, bw=4)
from render import AR_BLACK
tx1 = text_img("موظف مبيعات", AR_BLACK, 64, WHITE); tx2 = text_img("ذكي لمحلك", AR_BLACK, 64, CYAN, glow=8)
w1, w2, gap = tx1.width - 80, tx2.width - 80, 22
tot = w1 + w2 + gap; right = hp.width / 2 + tot / 2
hp.alpha_composite(tx1, (int(right - w1 - 40), (hp.height - tx1.height) // 2))
hp.alpha_composite(tx2, (int(right - w1 - gap - w2 - 40), (hp.height - tx2.height) // 2))
place(f, hp, W / 2, 225)

# ---------- ribbon ----------
rib = Image.new("RGBA", (820, 96), (0, 0, 0, 0))
g = gradient(820, 96, BLUE, CYAN).convert("RGBA")
m = Image.new("L", (820, 96), 0); ImageDraw.Draw(m).polygon([(30, 0), (820, 0), (790, 96), (0, 96)], fill=255)
rib.paste(g, (0, 0), m)
rt = text_img("يرد ويبيع بدالك 24 ساعة", AR, 50, NAVY)
rib.alpha_composite(rt, ((820 - rt.width) // 2, (96 - rt.height) // 2))
place(f, rib.rotate(-1.5, expand=True, resample=Image.BICUBIC), W / 2, 345)

# ---------- devices: laptop + phone (left) ----------
def laptop():
    w, h = 470, 300
    im = Image.new("RGBA", (w + 80, h + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox, oy = 40, 10
    d.rounded_rectangle((ox, oy, ox + w, oy + h), 18, fill=(10, 16, 28, 255), outline=(120, 140, 170, 255), width=4)
    scr = (ox + 16, oy + 16, ox + w - 16, oy + h - 16)
    d.rectangle(scr, fill=(6, 14, 34, 255))
    # website on screen
    d.rectangle((scr[0], scr[1], scr[2], scr[1] + 26), fill=(14, 30, 60, 255))
    for k, col in enumerate([CYAN, BLUE, PURPLE]): d.ellipse((scr[0] + 10 + k * 18, scr[1] + 8, scr[0] + 20 + k * 18, scr[1] + 18), fill=col + (255,))
    hero = gradient(scr[2] - scr[0] - 30, 120, BLUE, PURPLE).convert("RGBA")
    mm = Image.new("L", hero.size, 0); ImageDraw.Draw(mm).rounded_rectangle((0, 0, *hero.size), 14, fill=255)
    im.paste(hero, (scr[0] + 15, scr[1] + 40), mm)
    t = text_img("موقعك", AR, 40, WHITE); im.alpha_composite(t, (int((scr[0] + scr[2]) / 2 - t.width / 2), scr[1] + 100 - t.height // 2))
    for k in range(3):
        cx0 = scr[0] + 20 + k * 140
        d.rounded_rectangle((cx0, scr[1] + 176, cx0 + 120, scr[1] + 250), 10, outline=CYAN + (180,), width=2)
        d.rounded_rectangle((cx0 + 12, scr[1] + 190, cx0 + 108, scr[1] + 222), 6, fill=(0, 102, 255, 160))
    # base
    d.polygon([(ox - 30, oy + h + 6), (ox + w + 30, oy + h + 6), (ox + w + 50, oy + h + 30), (ox - 50, oy + h + 30)], fill=(150, 165, 190, 255))
    d.rectangle((ox + w / 2 - 50, oy + h + 6, ox + w / 2 + 50, oy + h + 12), fill=(90, 105, 130, 255))
    return im

def phone():
    w, h = 190, 380
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); o = 20
    d.rounded_rectangle((o, o, o + w, o + h), 30, fill=(10, 16, 28, 255), outline=(150, 165, 190, 255), width=5)
    d.rounded_rectangle((o + 10, o + 12, o + w - 10, o + h - 12), 22, fill=(6, 14, 34, 255))
    d.rounded_rectangle((o + w / 2 - 26, o + 18, o + w / 2 + 26, o + 30), 6, fill=(10, 16, 28, 255))
    def bub(y, txt, bot):
        t = text_img(txt, AR, 22, WHITE)
        bw = min(t.width - 80 + 30, w - 30)
        x0 = o + w - 14 - bw if not bot else o + 14
        col = (0, 102, 255, 255) if bot else (30, 44, 70, 255)
        d.rounded_rectangle((x0, y, x0 + bw, y + 44), 18, fill=col)
        im.alpha_composite(t, (int(x0 + bw / 2 - t.width / 2), int(y + 22 - t.height / 2)))
    bub(o + 56, "متوفر؟", False)
    bub(o + 112, "إي، متوفر", True)
    bub(o + 168, "شكد التوصيل؟", False)
    bub(o + 224, "يوصل باچر", True)
    d.rounded_rectangle((o + 22, o + 290, o + w - 22, o + 336), 20, fill=CYAN + (255,))
    t = text_img("تم الطلب ✓", AR, 24, NAVY); im.alpha_composite(t, (int(o + w / 2 - t.width / 2), int(o + 313 - t.height / 2)))
    return im

lp = laptop(); php = phone()
# glow under devices
l, d = ov(); d.ellipse((40, 820, 560, 900), fill=CYAN + (90,)); f.alpha_composite(l.filter(ImageFilter.GaussianBlur(30)))
lp = lp.resize((int(lp.width * 0.86), int(lp.height * 0.86)), Image.LANCZOS)
place(f, lp, 262, 700)
place(f, php, 462, 720, 1, 0.9)

# ---------- feature pills (right column) ----------
FEAT = [("chat", "رد فوري: ماسنجر · إنستا · واتساب"), ("q", "يجاوب على أسئلة زبائنك"),
        ("grid", "يعرض منتجاتك وتفاصيلها"), ("cart", "يثبّت الطلبات بدالك"),
        ("clock", "شغّال 24 ساعة بدون عطلة"), ("globe", "موقع احترافي لمحلك")]
for i, (ic, txt) in enumerate(FEAT):
    p = glow_pill(470, 70, glow=8, bw=2)
    t = text_img(txt, AR, 29, WHITE)
    sc = min(1.0, 380 / (t.width - 80))
    if sc < 1: t = t.resize((int(t.width * sc), int(t.height * sc)), Image.LANCZOS)
    p.alpha_composite(t, (p.width - 40 - 74 - t.width + 40, (p.height - t.height) // 2))
    ico = icon(ic, 44); p.alpha_composite(ico, (p.width - 40 - 20 - 44, (p.height - 44) // 2))
    place(f, p, 800, 470 + i * 82)

# ---------- suitable for ----------
tag = Image.new("RGBA", (230, 70), (0, 0, 0, 0))
gg = gradient(230, 70, PURPLE, BLUE).convert("RGBA")
mm = Image.new("L", (230, 70), 0); ImageDraw.Draw(mm).rounded_rectangle((0, 0, 230, 70), 35, fill=255); tag.paste(gg, (0, 0), mm)
tt = text_img("مناسب لـ:", AR, 36, WHITE); tag.alpha_composite(tt, ((230 - tt.width) // 2, (70 - tt.height) // 2))
place(f, tag.rotate(6, expand=True, resample=Image.BICUBIC), 180, 930)
bar = glow_pill(900, 130, glow=12, bw=3)
cats = [("food", "المطاعم"), ("shirt", "محلات الملابس"), ("scissors", "الصالونات"), ("store", "المتاجر")]
seg = 900 / 4
dd = ImageDraw.Draw(bar)
for i, (ic, name) in enumerate(cats):
    cx = 40 + 900 - seg * (i + 0.5)
    ico = icon(ic, 48); bar.alpha_composite(ico, (int(cx - 24), 40 + 14))
    t = text_img(name, AR, 31, WHITE); bar.alpha_composite(t, (int(cx - t.width / 2), 40 + 52))
    if i: dd.line((40 + 900 - seg * i, 40 + 30, 40 + 900 - seg * i, 40 + 100), fill=(169, 184, 204, 110), width=2)
place(f, bar, W / 2, 1010)

# ---------- CTA ----------
cta = glow_pill(840, 112, glow=20, bw=4, grad_fill=(BLUE, (0, 170, 255)))
put_text_in(cta, "راسلنا هسه وجرّب البوت بنفسك", 44, WHITE)
place(f, cta, W / 2, 1150)

# ---------- trust badges ----------
TB = [("bolt", "رد بثانية"), ("clock", "شغّال 24/7"), ("shield", "مصمم حسب محلك")]
for i, (ic, txt) in enumerate(TB):
    p = glow_pill(310, 76, glow=8, bw=2)
    t = text_img(txt, AR, 29, WHITE)
    ico = icon(ic, 40)
    total = t.width - 80 + 50
    p.alpha_composite(t, (int(p.width / 2 + total / 2 - 50 - t.width + 40), (p.height - t.height) // 2))
    p.alpha_composite(ico, (int(p.width / 2 + total / 2 - 40), (p.height - 40) // 2))
    place(f, p, W / 2 + (1 - i) * 340, 1272)

f.convert("RGB").save("nexo-post.jpg", quality=93)
print("ok")
