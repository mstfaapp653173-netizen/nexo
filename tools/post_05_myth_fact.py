"""Image post 5 — idea 6: myth vs fact | layout: table/comparison board (two columns, 4 rows)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from render import text_img, gradient, rounded, place, NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, AR_BLACK, AR_REG, EN, EN_SB

W, H = 1080, 1350
OUT = sys.argv[1] if len(sys.argv) > 1 else "nexo-post.jpg"
DIM = (120, 132, 152)

# full-bleed background: navy with soft blue/purple glows
f = gradient(W, H, (8, 24, 58), NAVY, (22, 12, 54)).convert("RGBA")
for (x, y, r, c, a) in [(900, 160, 420, BLUE, 70), (120, 1250, 460, PURPLE, 60)]:
    g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse((x - r, y - r, x + r, y + r), fill=a)
    f.paste(Image.new("RGBA", (W, H), c + (255,)), (0, 0), g.filter(ImageFilter.GaussianBlur(160)))
l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
for x in range(0, W, 54):
    for y in range(0, H, 54): d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=WHITE + (14,))
f.alpha_composite(l)

def right(img, y, xr=W - 70):
    f.alpha_composite(img, (int(xr - img.width + 40), int(y - img.height / 2)))

# header
place(f, text_img("NEXO", EN, 44, WHITE, rtl=False), 125, 82)
tag = rounded(270, 62, 31, DNAVY, border=(0, 212, 255, 200), shadow=False).copy()
tt = text_img("سمعتها قبل؟", AR, 30, CYAN); tag.alpha_composite(tt, ((tag.width - tt.width) // 2, (tag.height - tt.height) // 2))
place(f, tag, W - 175, 82)
right(text_img("4 أفكار غلط", AR_BLACK, 104, WHITE), 215)
right(text_img("عن البوت والموقع", AR_BLACK, 74, CYAN, glow=10), 330)

# board
BX0, BX1, BY0 = 60, W - 60, 425
COLW = (BX1 - BX0) // 2
ROWS = [("البوت بس للشركات الكبيرة", "يناسب أي محل، مطعم أو صالون"),
        ("البوت يرد بس رسالة ترحيب", "يجاوب، يعرض المنتجات ويثبّت الطلب"),
        ("لازم أبقى عالموبايل طول اليوم", "البوت يرد بدالك 24 ساعة"),
        ("صفحة الفيسبوك تكفي", "الموقع يخلّي الزبون يلگاك من گوگل")]
RH = 152; HEAD = 92
BH = HEAD + RH * len(ROWS)
board = Image.new("RGBA", (W, BH + 80), (0, 0, 0, 0)); bd = ImageDraw.Draw(board)
sh = Image.new("L", board.size, 0); ImageDraw.Draw(sh).rounded_rectangle((BX0, 50, BX1, 50 + BH), 44, fill=255)
board.paste(Image.new("RGBA", board.size, (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(24)).point(lambda v: int(v * 0.6)))
bd.rounded_rectangle((BX0, 40, BX1, 40 + BH), 44, fill=DNAVY + (255,), outline=(0, 212, 255, 110), width=3)
# fact column (left) tinted
fact = Image.new("L", board.size, 0); fd = ImageDraw.Draw(fact)
fd.rounded_rectangle((BX0, 40, BX1, 40 + BH), 44, fill=255); fd.rectangle((BX0 + COLW, 40, BX1, 40 + BH), fill=0)
board.paste(gradient(W, BH + 80, (0, 60, 150), (40, 20, 110)).convert("RGBA"), (0, 0), fact.point(lambda v: int(v * 0.55)))
# header row labels
mid_r = BX0 + COLW + COLW // 2; mid_l = BX0 + COLW // 2; hy = 40 + HEAD // 2
for txt, cx, col in [("الفكرة الشائعة", mid_r, GRAY), ("الحقيقة", mid_l, CYAN)]:
    im = text_img(txt, AR, 40, col); board.alpha_composite(im, (cx - im.width // 2, hy - im.height // 2))
bd.line((BX0 + 30, 40 + HEAD, BX1 - 30, 40 + HEAD), fill=(0, 212, 255, 120), width=3)
bd.line((BX0 + COLW, 40 + 20, BX0 + COLW, 40 + BH - 20), fill=(169, 184, 204, 60), width=2)

def wrap(txt, font, size, maxw):
    words = txt.split(); lines = [""]
    for w in words:
        cand = (lines[-1] + " " + w).strip()
        if text_img(cand, font, size).width - 80 <= maxw: lines[-1] = cand
        else: lines.append(w)
    return lines

def icon(kind):
    s = 64; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s // 2
    if kind == "x":
        d.ellipse((2, 2, s - 2, s - 2), fill=(40, 52, 78, 255), outline=DIM + (255,), width=3)
        d.line((c - 11, c - 11, c + 11, c + 11), fill=WHITE + (255,), width=6); d.line((c - 11, c + 11, c + 11, c - 11), fill=WHITE + (255,), width=6)
    else:
        d.ellipse((2, 2, s - 2, s - 2), fill=CYAN + (255,))
        d.line((c - 13, c + 1, c - 3, c + 11, c + 14, c - 10), fill=NAVY + (255,), width=7, joint="curve")
    return im

for i, (myth, truth) in enumerate(ROWS):
    y = 40 + HEAD + RH * i + RH // 2
    # myth (right column, RTL): icon at right edge, struck-through grey text
    ix = BX1 - 52
    ic = icon("x"); board.alpha_composite(ic, (ix - 32, y - 32))
    ls = wrap(myth, AR, 34, COLW - 120)
    for j, ln in enumerate(ls):
        t = text_img(ln, AR, 34, DIM)
        yy = y + (j - (len(ls) - 1) / 2) * 52
        x = ix - 46 - t.width + 40
        board.alpha_composite(t, (int(x), int(yy - t.height / 2)))
        bd.line((x + 40, yy + 4, x + t.width - 40, yy + 4), fill=DIM + (170,), width=2)
    # truth (left column): icon at its right edge, bold white text
    jx = BX0 + COLW - 52
    ic = icon("v"); board.alpha_composite(ic, (jx - 32, y - 32))
    ls = wrap(truth, AR, 34, COLW - 120)
    for j, ln in enumerate(ls):
        t = text_img(ln, AR, 34, WHITE)
        yy = y + (j - (len(ls) - 1) / 2) * 52
        board.alpha_composite(t, (int(jx - 46 - t.width + 40), int(yy - t.height / 2)))
    if i < len(ROWS) - 1:
        bd.line((BX0 + 30, y + RH // 2, BX1 - 30, y + RH // 2), fill=(169, 184, 204, 45), width=2)
f.alpha_composite(board, (0, BY0 - 40))

# footer CTA
fy = BY0 + BH + 80
right(text_img("الحقيقة أبسط مما تتوقع…", AR, 44, WHITE), fy)
btn = rounded(330, 84, 42, BLUE, grad=(BLUE, (0, 170, 255)), shadow=False).copy()
bt = text_img("اسألنا هسه", AR, 38, WHITE)
btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
f.alpha_composite(btn, (60 - 40, int(fy - btn.height / 2)))
place(f, text_img("موظف مبيعات ذكي + موقع احترافي  ·  nexodeveloper.net", AR_REG, 24, GRAY), W / 2, H - 40)

f.convert("RGB").save(OUT, quality=93)
print("ok", OUT, "footer y", fy)
