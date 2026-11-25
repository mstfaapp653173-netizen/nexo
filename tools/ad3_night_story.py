"""Reel 3 — concept 1: قصة زبون الساعة 2 بالليل (night-to-morning story, storybook timeline).
Usage: python3 ad3_night_story.py [t1 t2 ...]  (preview frames) | no args -> v3.mp4"""
import sys, os, math, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from style_ad import (background, brackets, word_img, blurred, site_card, bot_icon, bot_eyes,
                      gradient, text_img, rounded, place, ease_out, ease_back, prog, clamp,
                      NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, EN, EN_SB, W, H, FPS)
from render import AR_BLACK

DUR = 52.0
N = int(DUR * FPS)
CX, CY, TY = W // 2, 860, 1420
DIM = (110, 122, 140)

# speech segments (from silencedetect) -> display lines
SEG = [(0.0, 0.86), (1.35, 2.94), (3.28, 4.20), (4.44, 6.21), (6.61, 7.34), (7.55, 10.03), (10.43, 12.37),
       (12.77, 13.34), (13.64, 14.28), (14.75, 17.12), (17.40, 19.54), (19.94, 23.51), (23.86, 26.51),
       (26.74, 28.59), (28.78, 30.14), (30.43, 32.18), (32.56, 34.28), (34.67, 36.23), (36.46, 37.29),
       (37.48, 39.31), (39.65, 43.73), (44.10, 45.99), (46.26, 47.20)]
TEXT = [["تخيّل وياي…"], ["الساعة صارت", "ثنتين بالليل،"], ["محلك مسكّر،"], ["وإنت نايم", "ومرتاح بالبيت."],
        ["بهالوقت،"], ["واحد سهران", "دا يتصفّح صفحتك", "بالإنستا…"], ["عجبه قميص،", "ودزّلك رسالة:"],
        ["متوفر؟"], ["وشلون أطلب؟"], ["بالعادة،", "هالرسالة تبقى", "لحد الصبح…"],
        ["والزبون يمل،", "ويطلب من محل ثاني."], ["بس هالمرة،", "صفحتك بيها", "موظف مبيعات ذكي", "من نيكسو."],
        ["خلال ثانية وحدة،", "يرد عليه بكل لطف،"], ["يعرضله الألوان", "والقياسات،"], ["يجاوب على", "كل أسئلته،"],
        ["ياخذ العنوان،", "ويثبّت الطلب…"], ["بدون ما تحچي", "ولا كلمة."], ["الصبح،", "تگعد من النوم،"],
        ["تشرب جايك،"], ["وتلگى الطلب", "جاهز يستناك."],
        ["وإذا تريد زبائن جدد", "يلگونك بگوگل،", "نسوّيلك", "موقع احترافي هم."],
        ["دزّ هذا الفيديو", "لصاحب محل تعرفه…"], ["وراسلنا هسه."]]
ACCENT = {"تخيّل", "ثنتين", "بالليل،", "مسكّر،", "نايم", "سهران", "قميص،", "متوفر؟", "أطلب؟", "الصبح…", "ثاني.",
          "هالمرة،", "موظف", "مبيعات", "ذكي", "نيكسو.", "ثانية", "لطف،", "الألوان", "والقياسات،", "أسئلته،",
          "ويثبّت", "الطلب…", "كلمة.", "الصبح،", "جايك،", "جاهز", "بگوگل،", "احترافي", "دزّ", "تعرفه…", "هسه."}
VO_END = 48.27

LINE_T = []   # (start, end, [(word, accent, t)])
for (s, e), lines in zip(SEG, TEXT):
    allw = [w for ln in lines for w in ln.split()]
    tot = sum(len(w) + 1 for w in allw); acc = 0; k = 0
    starts = []
    for ln in lines:
        row = []
        for w in ln.split():
            row.append((w, w in ACCENT, s + (e - s) * acc / tot)); acc += len(w) + 1
        starts.append(row)
    for i, row in enumerate(starts):
        LINE_T.append([row[0][2], None, row])
for i, L in enumerate(LINE_T):
    L[1] = (LINE_T[i + 1][0] - 0.03) if i + 1 < len(LINE_T) else VO_END
    if i + 1 < len(LINE_T) and LINE_T[i + 1][0] - L[0] > 3: L[1] = L[0] + 2.6

def T(word):
    for s, e, row in LINE_T:
        for w, a, t in row:
            if w == word: return t
    raise KeyError(word)

T_BROWSE, T_USUAL, T_BOT = SEG[4][0], SEG[9][0], SEG[11][0]
T_CHAT, T_COLORS, T_ANS, T_ADDR, T_QUIET = SEG[12][0], SEG[13][0], SEG[14][0], SEG[15][0], SEG[16][0]
T_MORN, T_TEA, T_FOUND, T_WEB, T_SEND, T_OUT = SEG[17][0], SEG[18][0], SEG[19][0], SEG[20][0], SEG[21][0], 46.15

def captions(f, t, y=TY):
    for s, e, ws in LINE_T:
        if t < s - 0.06 or t > e or s >= T_OUT: continue
        out = 1 - prog(t, e - 0.18, 0.18) if e - s < 2.5 or True else 1
        imgs = [word_img(w, a) for w, a, _ in ws]
        gap = -40; total = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
        sc = min(1.0, 980 / max(total, 1)); x = W / 2 + total * sc / 2
        for (w, a, st), im in zip(ws, imgs):
            if t >= st - 0.06 or st < 0.7:
                p = 1.0 if st < 0.7 else ease_out(prog(t, st - 0.06, 0.22))
                place(f, blurred(w, a, int(round((1 - p) * 8))), x - im.width * sc / 2, y + (1 - p) * 24, p * out, sc * (1.08 - 0.08 * p))
            x -= (im.width + gap) * sc

def overlay(f):
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)

def pill(txt, size=42, border=(0, 212, 255, 220), fill=DNAVY, col=WHITE, font=AR, rtl=True):
    tx = text_img(txt, font, size, col, rtl=rtl)
    p = rounded(tx.width - 80 + 70, size + 50, (size + 50) // 2, fill, border=border, shadow=False).copy()
    p.alpha_composite(tx, ((p.width - tx.width) // 2, (p.height - tx.height) // 2))
    return p

def cust_bubble(txt, size=38):
    return pill(txt, size, border=(169, 184, 204, 120), fill=(22, 32, 52), col=WHITE)

def bot_bubble(txt, size=38):
    b = text_img(txt, AR, size, WHITE)
    bb = rounded(b.width - 80 + 60, size + 50, (size + 50) // 2, BLUE, grad=(BLUE, (0, 150, 255)), shadow=False).copy()
    bb.alpha_composite(b, ((bb.width - b.width) // 2, (bb.height - b.height) // 2))
    return bb

def pop(t, st, d=0.32): return ease_back(prog(t, st, d))

# ---------- icons ----------
@lru_cache(None)
def moon(s=300):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s, s), fill=WHITE + (255,))
    d.ellipse((s * 0.32, -s * 0.12, s * 1.22, s * 0.78), fill=(0, 0, 0, 0))
    return im

@lru_cache(None)
def shop_closed():
    s = 440; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((50, 180, 390, 410), 28, fill=WHITE + (255,))
    for k in range(6):
        x0 = 30 + k * 63; col = CYAN if k % 2 == 0 else WHITE
        d.pieslice((x0, 110, x0 + 63, 220), 0, 180, fill=col + (255,)); d.rectangle((x0, 90, x0 + 63, 166), fill=col + (255,))
    d.rounded_rectangle((85, 240, 355, 410), 10, fill=(14, 30, 58, 255))          # shutter
    for k in range(7): d.line((95, 262 + k * 21, 345, 262 + k * 21), fill=(60, 80, 110, 255), width=4)
    return im

@lru_cache(None)
def shirt(s=150, col=WHITE):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); u = s / 10
    d.polygon([(3.3*u, 1*u), (1*u, 2.4*u), (0.2*u, 4.4*u), (2*u, 5*u), (2.4*u, 4*u), (2.4*u, 9.2*u),
               (7.6*u, 9.2*u), (7.6*u, 4*u), (8*u, 5*u), (9.8*u, 4.4*u), (9*u, 2.4*u), (6.7*u, 1*u)], fill=col + (255,))
    d.pieslice((3.3*u, 0.1*u, 6.7*u, 2.6*u), 0, 180, fill=(0, 0, 0, 0))
    return im

@lru_cache(None)
def tea_glass():
    s = 300; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((20, 230, 280, 290), fill=WHITE + (255,))                         # saucer
    d.ellipse((40, 238, 260, 276), fill=(200, 214, 232, 255))
    # istikan glass (waisted)
    pts = [(95, 70), (205, 70), (190, 140), (215, 210), (195, 255), (105, 255), (85, 210), (110, 140)]
    d.polygon(pts, fill=(0, 212, 255, 90), outline=WHITE + (255,))
    tea = [(103, 110), (197, 110), (190, 140), (213, 210), (194, 252), (106, 252), (87, 210), (110, 140)]
    d.polygon(tea, fill=(0, 140, 230, 255))
    d.line(pts + [pts[0]], fill=WHITE + (255,), width=6)
    return im

def steam(f, cx, cy, t, a):
    lay, d = overlay(f)
    for k in range(3):
        x = cx - 50 + k * 50
        for j in range(14):
            yy = cy - j * 9 - (t * 40 % 20)
            xx = x + math.sin(j * 0.6 + t * 3 + k) * 12
            d.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), fill=WHITE + (int(110 * a * (1 - j / 14)),))
    f.alpha_composite(lay)

def zzz(f, cx, cy, t, a):
    for k in range(3):
        ph = (t * 0.55 + k / 3) % 1
        al = a * math.sin(ph * math.pi)
        place(f, text_img("z", EN, 60 + k * 14, CYAN, rtl=False), cx + ph * 70 + k * 10, cy - ph * 150, al)

def night_tint(f, a):
    if a <= 0.01: return
    lay, d = overlay(f); d.rectangle((0, 0, W, H), fill=(0, 0, 10, int(70 * a))); f.alpha_composite(lay)

def stars(f, t, a):
    if a <= 0.01: return
    lay, d = overlay(f)
    for k in range(26):
        x = (k * 397) % W; y = 60 + (k * 233) % 1700
        tw = 0.5 + 0.5 * math.sin(t * 2.2 + k)
        r = 3 + (k % 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE + (int(160 * a * tw),))
    f.alpha_composite(lay)

def phone(w=620, h=840):
    return rounded(w, h, 70, DNAVY, border=(0, 212, 255, 120))

def clock_face(f, cx, cy, r, hours, a, col=WHITE):
    lay, d = overlay(f); A = int(255 * a)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=DNAVY + (int(230 * a),), outline=col + (A,), width=12)
    for k in range(12):
        ang = math.radians(k * 30); r1 = r - (40 if k % 3 == 0 else 26)
        d.line((cx + r1 * math.sin(ang), cy - r1 * math.cos(ang), cx + (r - 16) * math.sin(ang), cy - (r - 16) * math.cos(ang)),
               fill=(GRAY if k % 3 else CYAN) + (A,), width=8 if k % 3 == 0 else 5)
    ha = math.radians((hours % 12) * 30); ma = math.radians((hours % 1) * 360)
    d.line((cx, cy, cx + r * 0.5 * math.sin(ha), cy - r * 0.5 * math.cos(ha)), fill=WHITE + (A,), width=18)
    d.line((cx, cy, cx + r * 0.75 * math.sin(ma), cy - r * 0.75 * math.cos(ma)), fill=CYAN + (A,), width=10)
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=CYAN + (A,))
    f.alpha_composite(lay)

# ---------- scenes ----------
def scene_hook(f, t):
    if t > T_BROWSE + 0.1: return
    out = 1 - prog(t, T_BROWSE - 0.35, 0.3)
    # title card (fully visible on frame 0 = cover)
    place(f, text_img("قصة زبون", AR_BLACK, 132, WHITE), CX, 300, out)
    place(f, text_img("بنص الليل", AR_BLACK, 132, CYAN, glow=10), CX, 450, out)
    place(f, shop_closed(), CX, CY + 60 + math.sin(t * 2.4) * 5, out, 0.92)
    brackets(f, CX, CY + 40, 600, -1.0, t, out=out)
    place(f, moon(170), CX + 220, CY - 170, out)
    tag = pill("مسكّر", 44, border=(169, 184, 204, 200), fill=(22, 32, 52), col=GRAY)
    place(f, tag, CX - 170, CY + 330, pop(t, SEG[2][0]) * out)
    place(f, pill("2:00 AM", 46, font=EN, rtl=False, col=CYAN), CX + (170 if t > SEG[2][0] else 0) * ease_out(prog(t, SEG[2][0], 0.3)), CY + 330, out)
    if t > SEG[3][0] - 0.2: zzz(f, CX + 330, CY - 50, t, out * prog(t, SEG[3][0], 0.3))

def scene_browse(f, t):
    if t < T_BROWSE - 0.2 or t > T_USUAL + 0.1: return
    out = 1 - prog(t, T_USUAL - 0.3, 0.25)
    pin = ease_out(prog(t, T_BROWSE, 0.4)); a = pin * out
    py = CY + 20 + (1 - pin) * 160
    place(f, phone(), CX, py, a)
    top = py - 420
    # header
    place(f, text_img("@yourshop", EN_SB, 40, WHITE, rtl=False), CX + 130, top + 60, a)
    lay, d = overlay(f)
    d.ellipse((CX - 250, top + 30, CX - 190, top + 90), outline=CYAN + (int(255 * a),), width=6)
    f.alpha_composite(lay)
    # product grid 3x2, scrolls a little while browsing
    scroll = ease_out(prog(t, SEG[5][0], 2.2)) * 60
    pick = 4
    hl = ease_back(prog(t, SEG[6][0], 0.45))
    for k in range(6):
        r, c = divmod(k, 3)
        gx = CX + 185 - c * 185; gy = top + 230 + r * 190 - scroll
        g = gradient(170, 170, *[(BLUE, CYAN), (BLUE, PURPLE), (CYAN, PURPLE)][k % 3]).convert("RGBA")
        m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 170, 170), 22, fill=255); g.putalpha(m)
        g.alpha_composite(shirt(110, WHITE if k != pick else WHITE), (30, 30))
        sc = 1 + (0.25 * hl if k == pick else 0)
        al = a * (1 - 0.6 * hl if k != pick else 1)
        place(f, g, gx, gy, al, sc)
    if hl > 0.01:
        heart = text_img("♥", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70, CYAN, rtl=False)
        place(f, heart, CX + 80, top + 300 - scroll, clamp(hl) * a, 0.6 + 0.4 * hl)
    ys = top + 640
    for st, txt, dy in [(SEG[7][0], "متوفر؟", 0), (SEG[8][0], "وشلون أطلب؟", 100)]:
        q = pop(t, st)
        if q > 0.01:
            b = cust_bubble(txt, 42)
            place(f, b, CX + 250 - b.width / 2, ys + dy, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    if t > SEG[6][0] + 1.0:   # notification chip
        q = pop(t, SEG[6][0] + 1.0)
        n = pill("رسالة جديدة", 36, col=CYAN)
        place(f, n, CX, top - 70, clamp(q * 1.5) * a, 0.8 + 0.2 * q)

def scene_usual(f, t):
    if t < T_USUAL - 0.2 or t > T_BOT + 0.1: return
    out = 1 - prog(t, T_BOT - 0.3, 0.25)
    pin = ease_out(prog(t, T_USUAL, 0.4)); a = pin * out
    hrs = 2 + 7 * ease_out(prog(t, T("هالرسالة"), 2.4))
    clock_face(f, CX, CY + 80, 250, hrs, a)
    hh = int(hrs); mm = int((hrs % 1) * 60)
    place(f, pill(f"{hh}:{mm:02d} AM", 46, font=EN, rtl=False, col=GRAY, border=(169, 184, 204, 160)), CX, CY + 400, a)
    # unanswered message card above the clock
    leave = ease_out(prog(t, SEG[10][0] + 0.9, 0.9))
    b = cust_bubble("متوفر؟ وشلون أطلب؟", 44)
    place(f, b, CX + leave * 380, CY - 330, a * (1 - leave))
    place(f, text_img("بدون رد", AR, 40, DIM), CX, CY - 235, a * (1 - leave) * prog(t, T_USUAL + 0.5, 0.3))
    if leave > 0.05:
        place(f, pill("راح لمحل ثاني", 44, border=(169, 184, 204, 140), fill=(22, 32, 52), col=DIM), CX, CY - 300, leave * a)

def scene_bot(f, t):
    if t < T_BOT - 0.2 or t > T_CHAT + 0.1: return
    out = 1 - prog(t, T_CHAT - 0.3, 0.25)
    flash = prog(t, T_BOT, 0.15) * (1 - prog(t, T_BOT + 0.15, 0.4))
    if flash > 0:
        lay, d = overlay(f); d.rectangle((0, 0, W, H), fill=CYAN + (int(60 * flash),)); f.alpha_composite(lay)
    p = ease_back(prog(t, T("موظف") - 0.6, 0.5))
    a = clamp(p * 1.5) * out; sc = 0.7 + 0.3 * p
    place(f, bot_icon(), CX, CY, a, sc); bot_eyes(f, CX, CY, sc, t, a)
    brackets(f, CX, CY, 640, T("موظف") - 0.6, t, out=out)
    place(f, pill("NEXO AI", 46, font=EN, rtl=False, col=CYAN), CX, CY + 360, a)

CHAT = [("c", "متوفر؟ وشلون أطلب؟", T_CHAT - 0.1), ("b", "هلا بيك! إي متوفر، تدلل", T("ثانية") + 0.2),
        ("sw", "", T_COLORS + 0.2), ("c", "شنو نوع القماش؟", T_ANS - 0.1), ("b", "قطن، خفيف ومريح", T_ANS + 0.7),
        ("c", "بغداد - المنصور", T_ADDR + 0.1), ("b", "تم تثبيت طلبك ✓", T("ويثبّت"))]

def color_row(t, st):
    im = Image.new("RGBA", (560, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, col in enumerate([WHITE, CYAN, BLUE, PURPLE, (30, 40, 60)]):
        q = clamp(ease_back(prog(t, st + k * 0.08, 0.3)))
        r = 34 * q; x = 500 - k * 100; y = 50
        if r > 1: d.ellipse((x - r, y - r, x + r, y + r), fill=col + (255,), outline=WHITE + (200,), width=3)
    for k, s_ in enumerate(["S", "M", "L", "XL"]):
        q = clamp(ease_back(prog(t, st + 0.4 + k * 0.08, 0.3)))
        if q < 0.02: continue
        chip = rounded(96, 64, 32, DNAVY if k != 2 else BLUE, border=(0, 212, 255, 200), shadow=False)
        x = 440 - k * 120
        im.alpha_composite(chip, (int(x - chip.width / 2), 150 - chip.height // 2))
        tx = text_img(s_, EN, 34, WHITE, rtl=False)
        im.alpha_composite(tx, (int(x - tx.width / 2), 150 - tx.height // 2))
    return im

def scene_chat(f, t):
    if t < T_CHAT - 0.2 or t > T_MORN + 0.1: return
    out = 1 - prog(t, T_MORN - 0.3, 0.25)
    pin = ease_out(prog(t, T_CHAT - 0.2, 0.35)); a = pin * out
    py = CY + 20
    place(f, phone(), CX, py, a)
    top = py - 420
    place(f, text_img("2:01 AM", EN_SB, 40, GRAY, rtl=False), CX + 170, top + 55, a)
    place(f, moon(54), CX - 220, top + 55, a)
    # stack messages, scroll up when overflowing
    items = []
    for kind, txt, st in CHAT:
        if t < st - 0.05: continue
        if kind == "sw": im = color_row(t, st); h = 210
        elif kind == "c": im = cust_bubble(txt); h = 104
        else: im = bot_bubble(txt, 40 if "✓" in txt else 38); h = 104
        items.append((kind, im, st, h))
    total = sum(h for _, _, _, h in items)
    avail = 640
    shift = max(0, total - avail)
    y = top + 130 - shift
    for kind, im, st, h in items:
        q = pop(t, st, 0.3)
        cy = y + h / 2; y += h
        if cy < top + 100: continue
        if kind == "c": x = CX + 270 - im.width / 2 + 40
        elif kind == "b": x = CX - 270 + im.width / 2 - 40
        else: x = CX
        place(f, im, x, cy, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    if T("ثانية") - 0.3 < t < T_COLORS:
        q = pop(t, T("ثانية") - 0.3)
        place(f, pill("00:01", 44, font=EN, rtl=False, col=CYAN), CX, top - 60, clamp(q * 1.5) * a, 0.8 + 0.2 * q)
    if t > T_QUIET:
        q = pop(t, T_QUIET, 0.4)
        place(f, pill("وإنت نايم", 44, col=CYAN), CX, top - 60, clamp(q * 1.5) * a, 0.8 + 0.2 * q)
        zzz(f, CX + 200, top - 90, t, a * clamp(q))

def scene_morning(f, t):
    if t < T_MORN - 0.2 or t > T_WEB + 0.1: return
    out = 1 - prog(t, T_WEB - 0.3, 0.25)
    rise = ease_out(prog(t, T_MORN, 1.6)); a = clamp(prog(t, T_MORN - 0.1, 0.4)) * out
    # sun rising with soft glow
    sy = CY + 360 - rise * 320
    lay, d = overlay(f)
    for r, al in [(330, 30), (250, 50), (180, 90)]:
        d.ellipse((CX - r, sy - r, CX + r, sy + r), fill=CYAN + (int(al * a),))
    d.ellipse((CX - 130, sy - 130, CX + 130, sy + 130), fill=WHITE + (int(255 * a),))
    for k in range(12):
        ang = math.radians(k * 30 + t * 12)
        d.line((CX + 170 * math.cos(ang), sy + 170 * math.sin(ang), CX + 215 * math.cos(ang), sy + 215 * math.sin(ang)),
               fill=WHITE + (int(200 * a),), width=10)
    f.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
    place(f, pill("8:00 AM", 46, font=EN, rtl=False, col=CYAN), CX, 300, a)
    if t > T_TEA - 0.1:
        q = pop(t, T_TEA, 0.4)
        place(f, tea_glass(), CX + 300, CY + 300, clamp(q * 1.5) * a, (0.6 + 0.2 * q))
        steam(f, CX + 300, CY + 200, t, clamp(q) * a)
    if t > T_FOUND - 0.1:
        q = ease_out(prog(t, T_FOUND, 0.45))
        card = rounded(760, 230, 40, DNAVY, border=(0, 212, 255, 220)).copy()
        t1 = text_img("طلب جديد مثبّت ✓", AR, 52, CYAN)
        t2 = text_img("قميص • قياس L • المنصور", AR, 38, WHITE)
        t3 = text_img("وصل الساعة 2:03 AM", AR, 32, GRAY)
        card.alpha_composite(t1, (card.width - 70 - t1.width + 40, 40 + 18 - 30))
        card.alpha_composite(t2, (card.width - 70 - t2.width + 40, 40 + 100 - 30))
        card.alpha_composite(t3, (card.width - 70 - t3.width + 40, 40 + 160 - 30))
        place(f, card, CX, 450 - (1 - q) * 200, q * out)

def scene_web(f, t):
    if t < T_WEB - 0.1 or t > T_SEND + 0.1: return
    out = 1 - prog(t, T_SEND - 0.3, 0.25)
    p = ease_out(prog(t, T_WEB, 0.4)); a = p * out
    bar = rounded(840, 110, 55, DNAVY, border=(0, 212, 255, 180), shadow=False).copy()
    q = "محل ملابس ببغداد"
    nchar = int(clamp((t - T_WEB - 0.3) / 1.4) * len(q))
    if nchar:
        tx = text_img(q[:nchar], AR, 46, WHITE)
        bar.alpha_composite(tx, (bar.width - 90 - tx.width + 40, (bar.height - tx.height) // 2))
    dd = ImageDraw.Draw(bar)
    dd.ellipse((70, 38, 110, 78), outline=CYAN + (255,), width=6); dd.line((104, 72, 122, 90), fill=CYAN + (255,), width=6)
    place(f, bar, CX, 330, a)
    st = T("نسوّيلك") - 0.3
    if t > st - 0.1:
        q2 = ease_back(prog(t, st, 0.45))
        place(f, site_card(1), CX, CY + 100, clamp(q2 * 1.5) * out, 0.6 + 0.2 * q2)
    else:
        # search results skeleton while typing
        lay, d = overlay(f)
        for k in range(3):
            y = 480 + k * 150; al = int(120 * a * prog(t, T_WEB + 0.6 + k * 0.2, 0.3))
            d.rounded_rectangle((150, y, 930, y + 110), 30, fill=(14, 30, 58, al))
            d.rounded_rectangle((420, y + 30, 880, y + 50), 10, fill=GRAY + (al,))
            d.rounded_rectangle((560, y + 66, 880, y + 82), 8, fill=GRAY + (al // 2,))
        f.alpha_composite(lay)

def scene_send(f, t):
    if t < T_SEND - 0.1 or t > T_OUT + 0.4: return
    out = 1 - prog(t, T_OUT, 0.3)
    p = ease_back(prog(t, T_SEND, 0.45))
    k = t - T_SEND
    x = CX + math.sin(k * 2.2) * 120; y = CY - 40 - k * 40
    s = 150 * (0.6 + 0.4 * p)
    lay, d = overlay(f); al = int(255 * clamp(p * 1.5) * out)
    pts = [(x + s, y - s * 0.3), (x - s, y - s * 0.05), (x - s * 0.35, y + s * 0.15), (x - s * 0.2, y + s * 0.7)]
    d.polygon([pts[0], pts[1], pts[2]], fill=WHITE + (al,)); d.polygon([pts[0], pts[2], pts[3]], fill=CYAN + (al,))
    for j in range(4):
        tx = x - s - 40 - j * 50; ty = y + 20 + j * 18
        d.ellipse((tx - 8, ty - 8, tx + 8, ty + 8), fill=CYAN + (int(al * (1 - j / 4)),))
    f.alpha_composite(lay)
    place(f, pill("دزّه لصاحب محل تعرفه", 50), CX, CY + 300, ease_out(prog(t, T("لصاحب"), 0.3)) * out)

def scene_outro(f, t):
    if t < T_OUT - 0.1: return
    p = ease_out(prog(t, T_OUT, 0.55))
    logo = text_img("NEXO", EN, 260, WHITE, rtl=False)
    if p < 1:
        logo = logo.copy(); m = Image.new("L", logo.size, 0)
        ImageDraw.Draw(m).rectangle((int(logo.width * (1 - p)), 0, logo.width, logo.height), fill=255)
        logo.putalpha(Image.composite(logo.getchannel("A"), Image.new("L", logo.size, 0), m))
    place(f, logo, CX, 640, clamp(p * 2))
    place(f, text_img("نيكسو", AR, 56, WHITE), CX + 260, 780, ease_out(prog(t, T_OUT + 0.3, 0.35)))
    q = ease_out(prog(t, T_OUT + 0.5, 0.4))
    if q > 0.01:
        lay, d = overlay(f); half = 160 * q
        d.line((CX - half, 870, CX + half, 870), fill=CYAN + (int(255 * q),), width=5); f.alpha_composite(lay)
    ws = [("زبونك", True, T_OUT + 0.9), ("ينخدم", False, T_OUT + 1.2), ("وإنت", False, T_OUT + 1.5), ("نايم", True, T_OUT + 1.8)]
    imgs = [word_img(w, a) for w, a, _ in ws]; gap = -40
    total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    sc = min(1.0, 960 / total); x = W / 2 + total * sc / 2
    for (w, a, st), im in zip(ws, imgs):
        r = ease_out(prog(t, st, 0.26))
        if r > 0.01: place(f, blurred(w, a, int(round((1 - r) * 8))), x - im.width * sc / 2, 1040 + (1 - r) * 24, r, sc)
        x -= (im.width + gap) * sc
    c = ease_back(prog(t, T_OUT + 2.3, 0.45))
    if c > 0.01:
        btn = rounded(640, 140, 70, BLUE, grad=(BLUE, (0, 160, 255))).copy()
        bt = text_img("راسلنا هسه", AR, 70, WHITE)
        btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
        pulse = 1 + 0.035 * math.sin(t * 6) * prog(t, T_OUT + 2.8, 0.3)
        place(f, btn, CX, 1300, clamp(c * 1.4), (0.8 + 0.2 * c) * pulse)
    dd = ease_out(prog(t, T_OUT + 2.7, 0.4))
    place(f, text_img("WhatsApp  07751027553", EN_SB, 50, WHITE, rtl=False), CX, 1490, dd)
    place(f, text_img("nexodeveloper.net", EN_SB, 46, CYAN, rtl=False), CX, 1570, dd)
    place(f, text_img("Connect to the Future.", EN_SB, 40, GRAY, rtl=False), CX, 1680, ease_out(prog(t, T_OUT + 3.2, 0.5)))

def frame(i):
    t = i / FPS
    f = background(t)
    night = 1 - prog(t, T_MORN, 1.2)
    night_tint(f, night); stars(f, t, night * (1 - prog(t, T_BOT - 0.2, 0.3) * (1 - prog(t, T_CHAT, 0.4))))
    scene_hook(f, t); scene_browse(f, t); scene_usual(f, t); scene_bot(f, t); scene_chat(f, t)
    scene_morning(f, t); scene_web(f, t); scene_send(f, t)
    scene_outro(f, t)
    if t < T_OUT: captions(f, t)
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]: frame(int(float(ts) * FPS)).save(f"p_{ts}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "v3.mp4"],
                         stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
