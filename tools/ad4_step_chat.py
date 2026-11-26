"""Reel 4 — concept 3: محادثة حقيقية ويا البوت خطوة بخطوة (stepper walkthrough, one chat panel per step).
Usage: python3 ad4_step_chat.py [t1 t2 ...]  (preview frames) | no args -> v4.mp4"""
import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from functools import lru_cache
from PIL import Image, ImageDraw
from style_ad import (background, brackets, word_img, blurred, site_card, bot_icon, bot_eyes, chat_icon,
                      gradient, text_img, rounded, place, ease_out, ease_back, prog, clamp,
                      NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, EN, EN_SB, W, H, FPS)
from render import AR_BLACK

DUR = 44.0
N = int(DUR * FPS)
CX = W // 2
TY = 1500                      # caption centre
PY = 880                       # chat panel centre
PW, PH = 860, 740
DIM = (110, 122, 140)

SEG = [(0.0, 0.63), (0.92, 2.52), (2.77, 3.69), (3.94, 6.96), (7.48, 8.25), (8.61, 9.36), (9.74, 10.57),
       (10.91, 13.11), (13.47, 13.97), (14.19, 14.93), (15.35, 16.12), (16.47, 17.61), (17.84, 20.66),
       (21.09, 21.95), (22.24, 23.19), (23.44, 26.11), (26.52, 27.35), (27.64, 28.69), (28.87, 29.75),
       (30.09, 32.22), (32.65, 34.14), (34.36, 35.89), (36.23, 38.20), (38.43, 39.26)]
TEXT = [["هلا بيك،"], ["خلّي أراويك", "محادثة وحدة،"], ["خطوة بخطوة،"], ["بين زبون", "وموظف المبيعات الذكي", "من نيكسو."],
        ["الخطوة الأولى:"], ["الزبون يكتب:"], ["عدكم توصيل؟"], ["والبوت يرد بكل لطف", "خلال ثانية:"],
        ["إي عدنا،"], ["وين منطقتك؟"], ["الخطوة الثانية:"], ["يسأل عن المنتج،"],
        ["والبوت يدزّله الصور", "والقياسات والتفاصيل."], ["الخطوة الثالثة:"], ["يختار اللي عجبه،"],
        ["والبوت ياخذ الاسم", "والعنوان ورقم التلفون."], ["الخطوة الرابعة:"], ["الطلب يتثبّت،"], ["ويوصلك إشعار."],
        ["كل هذا وإنت", "ما لمست الموبايل."], ["وإذا تريد زبائن", "من گوگل،"], ["نسوّيلك", "موقع احترافي هم."],
        ["دزّ هذا الفيديو", "لصاحب محل تعرفه،"], ["وراسلنا هسه."]]
ACCENT = {"هلا", "محادثة", "خطوة", "بخطوة،", "موظف", "المبيعات", "الذكي", "نيكسو.", "الأولى:", "توصيل؟", "لطف", "ثانية:",
          "الثانية:", "المنتج،", "الصور", "والقياسات", "الثالثة:", "عجبه،", "الاسم", "والعنوان", "التلفون.",
          "الرابعة:", "يتثبّت،", "إشعار.", "لمست", "الموبايل.", "گوگل،", "احترافي", "دزّ", "تعرفه،", "هسه."}
VO_END = 39.26
T_OUT = 38.35

LINE_T = []
for (s, e), lines in zip(SEG, TEXT):
    allw = [w for ln in lines for w in ln.split()]
    tot = sum(len(w) + 1 for w in allw); acc = 0
    for ln in lines:
        row = []
        for w in ln.split():
            row.append((w, w in ACCENT, s + (e - s) * acc / tot)); acc += len(w) + 1
        LINE_T.append([row[0][2], None, row])
for i, L in enumerate(LINE_T):
    L[1] = (LINE_T[i + 1][0] - 0.03) if i + 1 < len(LINE_T) else VO_END
    if i + 1 < len(LINE_T) and LINE_T[i + 1][0] - L[0] > 3: L[1] = L[0] + 2.6

def T(word, after=0.0):
    for s, e, row in LINE_T:
        for w, a, t in row:
            if w == word and t >= after: return t
    raise KeyError(word)

S1, S2, S3, S4, S_FREE, S_WEB, S_SEND = SEG[4][0], SEG[10][0], SEG[13][0], SEG[16][0], SEG[19][0], SEG[20][0], SEG[22][0]
STEPS = [(S1, S2, "الخطوة الأولى", "الزبون يسأل"), (S2, S3, "الخطوة الثانية", "يشوف المنتج"),
         (S3, S4, "الخطوة الثالثة", "يختار ويعطي معلوماته"), (S4, S_FREE, "الخطوة الرابعة", "الطلب يتثبّت")]

def captions(f, t, y=TY):
    for s, e, ws in LINE_T:
        if t < s - 0.06 or t > e or s >= T_OUT: continue
        out = 1 - prog(t, e - 0.18, 0.18)
        imgs = [word_img(w, a, 96) for w, a, _ in ws]
        gap = -40; total = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
        sc = min(1.0, 980 / max(total, 1)); x = W / 2 + total * sc / 2
        for (w, a, st), im in zip(ws, imgs):
            if t >= st - 0.06 or st < 0.7:
                p = 1.0 if st < 0.7 else ease_out(prog(t, st - 0.06, 0.22))
                src = im if p > 0.97 else im
                place(f, src, x - im.width * sc / 2, y + (1 - p) * 24, p * out, sc * (1.08 - 0.08 * p))
            x -= (im.width + gap) * sc

def overlay(f):
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)

@lru_cache(None)
def pill(txt, size=42, border=(0, 212, 255, 220), fill=DNAVY, col=WHITE, font=AR, rtl=True):
    tx = text_img(txt, font, size, col, rtl=rtl)
    p = rounded(tx.width - 80 + 70, size + 50, (size + 50) // 2, fill, border=border, shadow=False).copy()
    p.alpha_composite(tx, ((p.width - tx.width) // 2, (p.height - tx.height) // 2))
    return p

@lru_cache(None)
def cust_bubble(txt, size=44):
    return pill(txt, size, border=(169, 184, 204, 120), fill=(26, 38, 62), col=WHITE)

@lru_cache(None)
def bot_bubble(txt, size=44):
    b = text_img(txt, AR, size, WHITE)
    bb = rounded(b.width - 80 + 64, size + 54, (size + 54) // 2, BLUE, grad=(BLUE, (0, 150, 255)), shadow=False).copy()
    bb.alpha_composite(b, ((bb.width - b.width) // 2, (bb.height - b.height) // 2))
    return bb

def pop(t, st, d=0.32): return ease_back(prog(t, st, d))

# ---------- panel ----------
@lru_cache(None)
def panel():
    p = rounded(PW, PH, 54, DNAVY, border=(0, 212, 255, 150)).copy(); d = ImageDraw.Draw(p); o = 40
    d.rounded_rectangle((o, o, o + PW, o + 130), 54, fill=(12, 30, 62, 255))
    d.rectangle((o, o + 80, o + PW, o + 130), fill=(12, 30, 62, 255))
    d.line((o, o + 130, o + PW, o + 130), fill=(0, 212, 255, 90), width=3)
    # avatar (mini bot)
    ax, ay = o + PW - 95, o + 65
    d.ellipse((ax - 42, ay - 42, ax + 42, ay + 42), fill=BLUE + (255,))
    d.rounded_rectangle((ax - 26, ay - 16, ax + 26, ay + 18), 14, fill=WHITE + (255,))
    d.ellipse((ax - 15, ay - 5, ax - 5, ay + 5), fill=BLUE + (255,)); d.ellipse((ax + 5, ay - 5, ax + 15, ay + 5), fill=BLUE + (255,))
    nm = text_img("موظف المبيعات الذكي", AR, 38, WHITE)
    p.alpha_composite(nm, (ax - 70 - nm.width + 40, ay - 26 - nm.height // 2 + 4))
    st = text_img("متصل الآن", AR_REG_PATH(), 28, CYAN)
    p.alpha_composite(st, (ax - 70 - st.width + 40, ay + 22 - st.height // 2))
    d.ellipse((ax + 22, ay + 22, ax + 40, ay + 40), fill=CYAN + (255,), outline=DNAVY + (255,), width=3)
    return p

def AR_REG_PATH():
    from render import AR_REG; return AR_REG

def typing(f, x, y, t, a):
    b = rounded(150, 80, 40, (26, 38, 62), shadow=False)
    place(f, b, x, y, a)
    lay, d = overlay(f)
    for k in range(3):
        yy = y - 8 * max(0, math.sin(t * 9 - k * 0.9)); xx = x - 34 + k * 34
        d.ellipse((xx - 10, yy - 10, xx + 10, yy + 10), fill=GRAY + (int(255 * a),))
    f.alpha_composite(lay)

def stepper(f, t, a):
    if a <= 0.01: return
    lay, d = overlay(f); A = int(255 * a); y = 420
    xs = [CX + 255 - k * 170 for k in range(4)]
    cur = sum(1 for s, _, _, _ in STEPS if t >= s - 0.05) - 1
    done_all = t >= S_FREE - 0.05
    for k in range(3):
        fill = clamp((t - STEPS[k + 1][0] + 0.4) / 0.4) if cur > k else 0
        d.line((xs[k] - 30, y, xs[k + 1] + 30, y), fill=(60, 80, 110, A), width=6)
        if fill > 0: d.line((xs[k] - 30, y, xs[k] - 30 - (xs[k] - xs[k + 1] - 60) * fill, y), fill=CYAN + (A,), width=6)
    f.alpha_composite(lay)
    for k, x in enumerate(xs):
        if k < cur or done_all: im = dot_img("done")
        elif k == cur: im = dot_img("active", k + 1)
        else: im = dot_img("todo", k + 1)
        sc = 1.0 + (0.12 * math.sin(t * 5) if (k == cur and not done_all) else 0)
        place(f, im, x, y, a, sc)

@lru_cache(None)
def dot_img(kind, n=0):
    s = 110; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s // 2
    if kind == "done":
        d.ellipse((c - 30, c - 30, c + 30, c + 30), fill=CYAN + (255,))
        d.line((c - 14, c, c - 3, c + 12, c + 15, c - 12), fill=NAVY + (255,), width=8, joint="curve")
    elif kind == "active":
        d.ellipse((c - 44, c - 44, c + 44, c + 44), fill=(0, 102, 255, 70))
        d.ellipse((c - 32, c - 32, c + 32, c + 32), fill=BLUE + (255,), outline=CYAN + (255,), width=4)
        tx = text_img(str(n), EN, 36, WHITE, rtl=False); im.alpha_composite(tx, (c - tx.width // 2, c - tx.height // 2 - 2))
    else:
        d.ellipse((c - 30, c - 30, c + 30, c + 30), fill=DNAVY + (255,), outline=(90, 110, 140, 255), width=4)
        tx = text_img(str(n), EN, 32, GRAY, rtl=False); im.alpha_composite(tx, (c - tx.width // 2, c - tx.height // 2 - 2))
    return im

def header(f, t):
    for s, e, title, sub in STEPS:
        if t < s - 0.1 or t > e + 0.05: continue
        p = ease_out(prog(t, s - 0.05, 0.35)); out = 1 - prog(t, e - 0.25, 0.2)
        a = p * out
        place(f, text_img(title, AR_BLACK, 92, WHITE), CX + (1 - p) * 60, 215, a)
        place(f, text_img(sub, AR, 48, CYAN), CX - (1 - p) * 60, 318, a)

# ---------- chat content per step ----------
TOP = PY - PH // 2 + 195     # first message row y
RX = CX + PW // 2 - 40       # right edge for customer
LX = CX - PW // 2 + 40       # left edge for bot

def msg(f, im, side, y, t, st, a):
    q = pop(t, st, 0.3)
    if q <= 0.01: return
    x = RX - im.width / 2 + 40 if side == "c" else LX + im.width / 2 - 40
    place(f, im, x + (1 - clamp(q)) * (40 if side == "c" else -40), y, clamp(q * 1.5) * a, 0.85 + 0.15 * q)

@lru_cache(None)
def product_card(n_tiles, n_sizes, details):
    w, h = 540, 390
    c = rounded(w, h, 36, (14, 34, 70), border=(0, 212, 255, 160), shadow=False).copy(); o = 40
    grads = [(BLUE, CYAN), (PURPLE, BLUE), (CYAN, PURPLE)]
    for k in range(n_tiles):
        g = gradient(150, 150, *grads[k]).convert("RGBA")
        m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 150, 150), 22, fill=255)
        g.putalpha(m)
        gd = ImageDraw.Draw(g)   # simple tee silhouette
        u = 15
        gd.polygon([(5*u-12, 2*u), (2*u, 3*u), (1*u, 5*u), (3*u, 5.6*u), (3.2*u, 4.6*u), (3.2*u, 8.6*u),
                    (6.8*u, 8.6*u), (6.8*u, 4.6*u), (7*u, 5.6*u), (9*u, 5*u), (8*u, 3*u), (5*u+12, 2*u)], fill=WHITE + (235,))
        c.alpha_composite(g, (o + w - 30 - 150 - k * 165, o + 28))
    for k in range(n_sizes):
        s_ = ["S", "M", "L", "XL"][k]
        chip = rounded(96, 62, 31, DNAVY if k != 2 else BLUE, border=(0, 212, 255, 200), shadow=False)
        x = o + w - 30 - 48 - k * 122
        c.alpha_composite(chip, (int(x - chip.width / 2), o + 240 - chip.height // 2))
        tx = text_img(s_, EN, 32, WHITE, rtl=False)
        c.alpha_composite(tx, (int(x - tx.width / 2), o + 240 - tx.height // 2))
    if details:
        tx = text_img("قطن • خفيف • مريح", AR, 36, WHITE)
        c.alpha_composite(tx, (o + w - 30 - tx.width + 40, o + 325 - tx.height // 2))
    return c

@lru_cache(None)
def form_card(n):
    w, h = 560, 330
    c = rounded(w, h, 36, (14, 34, 70), border=(0, 212, 255, 160), shadow=False).copy(); d = ImageDraw.Draw(c); o = 40
    for k, lab in enumerate(["الاسم", "العنوان", "رقم التلفون"]):
        y = o + 60 + k * 100
        d.rounded_rectangle((o + 30, y - 36, o + w - 30, y + 36), 24, fill=(7, 19, 38, 255),
                            outline=(0, 212, 255, 200) if k < n else (90, 110, 140, 255), width=3)
        tx = text_img(lab, AR, 36, WHITE if k < n else GRAY)
        c.alpha_composite(tx, (o + w - 60 - tx.width + 40, y - tx.height // 2))
        if k < n:
            ck = dot_img("done"); c.alpha_composite(ck, (o + 70 - ck.width // 2, y - ck.height // 2))
    return c

def scene_steps(f, t):
    if t < S1 - 0.3 or t > S_FREE + 0.3: return
    pin = ease_out(prog(t, S1 - 0.3, 0.4)); out = 1 - prog(t, S_FREE - 0.1, 0.3)
    a = pin * out
    place(f, panel(), CX, PY + (1 - pin) * 120, a)
    stepper(f, t, pin * (1 - prog(t, S_WEB - 0.3, 0.3)))
    header(f, t)
    # which step's content is visible (fade/slide between steps)
    for k, (s, e, _, _) in enumerate(STEPS):
        if t < s - 0.1 or t > e + 0.05: continue
        so = 1 - prog(t, e - 0.25, 0.22)
        ca = a * so
        y0 = TOP - prog(t, e - 0.25, 0.22) * 60
        if k == 0:
            msg(f, cust_bubble("عدكم توصيل؟"), "c", y0 + 20, t, SEG[6][0] - 0.1, ca)
            if SEG[7][0] < t < SEG[8][0] - 0.05:
                typing(f, LX + 75, y0 + 140, t, ca * prog(t, SEG[7][0], 0.2))
            msg(f, bot_bubble("إي عدنا، وين منطقتك؟"), "b", y0 + 140, t, SEG[8][0] - 0.05, ca)
            if t > T("ثانية:") - 0.2:
                q = pop(t, T("ثانية:") - 0.2)
                place(f, pill("رد خلال ثانية", 42, col=CYAN), CX, PY + PH // 2 + 95, clamp(q * 1.5) * ca, 0.8 + 0.2 * q)
        elif k == 1:
            msg(f, cust_bubble("عندكم هذا التيشيرت؟"), "c", y0 + 20, t, SEG[11][0], ca)
            st = SEG[12][0] + 0.2
            if t > st:
                nt = 1 + (t > T("الصور") + 0.15) + (t > T("الصور") + 0.45)
                ns = 0 if t < T("والقياسات") else min(4, 1 + int((t - T("والقياسات")) / 0.15))
                det = t > T("والتفاصيل.")
                card = product_card(nt, ns, det)
                msg(f, card, "b", y0 + 120 + card.height / 2 - 40, t, st, ca)
        elif k == 2:
            msg(f, cust_bubble("آخذ الأزرق، قياس L"), "c", y0 + 20, t, SEG[14][0], ca)
            st = SEG[15][0] + 0.1
            if t > st:
                n = (t > T("الاسم")) + (t > T("والعنوان")) + (t > T("التلفون."))
                card = form_card(n)
                msg(f, card, "b", y0 + 120 + card.height / 2 - 40, t, st, ca)
        else:
            msg(f, bot_bubble("تم تثبيت طلبك ✓"), "b", y0 + 20, t, SEG[17][0] + 0.2, ca)
            msg(f, cust_bubble("تسلم، شكراً"), "c", y0 + 150, t, SEG[17][0] + 1.0, ca)
            if t > SEG[18][0]:
                q = ease_out(prog(t, SEG[18][0], 0.45))
                nb = notif_card()
                place(f, nb, CX, PY + 170 + (1 - q) * 140, q * ca)

@lru_cache(None)
def notif_card():
    w, h = 760, 170
    c = rounded(w, h, 40, (16, 40, 84), border=(0, 212, 255, 230)).copy(); d = ImageDraw.Draw(c); o = 40
    ix = o + w - 85; iy = o + h // 2
    d.rounded_rectangle((ix - 45, iy - 45, ix + 45, iy + 45), 24, fill=BLUE + (255,))
    # bell
    d.pieslice((ix - 26, iy - 30, ix + 26, iy + 22), 180, 360, fill=WHITE + (255,))
    d.rectangle((ix - 26, iy - 5, ix + 26, iy + 14), fill=WHITE + (255,))
    d.rectangle((ix - 32, iy + 12, ix + 32, iy + 20), fill=WHITE + (255,))
    d.ellipse((ix - 9, iy + 20, ix + 9, iy + 36), fill=WHITE + (255,))
    t1 = text_img("طلب جديد مثبّت ✓", AR, 46, WHITE)
    t2 = text_img("من نيكسو • هسه", AR_REG_PATH(), 30, CYAN)
    c.alpha_composite(t1, (ix - 75 - t1.width + 40, iy - 28 - t1.height // 2))
    c.alpha_composite(t2, (ix - 75 - t2.width + 40, iy + 34 - t2.height // 2))
    return c

# ---------- hook ----------
def scene_hook(f, t):
    if t > S1 + 0.1: return
    out = 1 - prog(t, S1 - 0.35, 0.3)
    place(f, text_img("محادثة وحدة", AR_BLACK, 136, WHITE), CX, 290, out)
    place(f, text_img("خطوة بخطوة", AR_BLACK, 136, CYAN, glow=10), CX, 450, out)
    cy = 900
    morph = prog(t, T("وموظف") - 0.2, 0.35)
    if morph < 1:
        place(f, chat_icon(), CX, cy + math.sin(t * 2.4) * 6, out * (1 - morph), 0.95 - 0.2 * morph)
    if morph > 0:
        sc = 0.75 + 0.2 * ease_back(morph)
        place(f, bot_icon(), CX, cy, out * morph, sc); bot_eyes(f, CX, cy, sc, t, out * morph)
    brackets(f, CX, cy, 620, -1.0, t, out=out)
    # 4 step dots preview (cover shows them)
    lay, d = overlay(f); A = int(255 * out); y = 1270
    xs = [CX + 210 - k * 140 for k in range(4)]
    d.line((xs[3], y, xs[0], y), fill=(60, 80, 110, A), width=6)
    f.alpha_composite(lay)
    for k, x in enumerate(xs):
        lit = t > SEG[2][0] + k * 0.18
        place(f, dot_img("active" if lit else "todo", k + 1), x, y, out, 1.0 + 0.15 * pop(t, SEG[2][0] + k * 0.18) * (1 - prog(t, SEG[2][0] + k * 0.18 + 0.3, 0.3)))
    if t > SEG[3][0] + 1.2:
        q = pop(t, SEG[3][0] + 1.2)
        place(f, pill("NEXO AI", 44, font=EN, rtl=False, col=CYAN), CX, 1150, clamp(q * 1.5) * out, 0.8 + 0.2 * q)

# ---------- hands-free ----------
@lru_cache(None)
def phone_icon():
    w, h = 300, 520
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); o = 20
    d.rounded_rectangle((o, o, o + w, o + h), 54, fill=WHITE + (255,))
    d.rounded_rectangle((o + 22, o + 50, o + w - 22, o + h - 50), 30, fill=NAVY + (255,))
    d.rounded_rectangle((o + w / 2 - 40, o + 20, o + w / 2 + 40, o + 32), 6, fill=NAVY + (255,))
    return im

def scene_free(f, t):
    if t < S_FREE - 0.2 or t > S_WEB + 0.1: return
    out = 1 - prog(t, S_WEB - 0.3, 0.25)
    p = ease_back(prog(t, S_FREE, 0.45)); a = clamp(p * 1.5) * out
    cy = 880
    place(f, phone_icon(), CX, cy, a, 0.8 + 0.2 * p)
    # four ticks stacking on the phone screen
    for k in range(4):
        q = pop(t, S_FREE + 0.3 + k * 0.22, 0.3)
        if q > 0.01:
            place(f, dot_img("done"), CX - 70, cy - 150 + k * 100, clamp(q * 1.5) * out, 0.9 * (0.8 + 0.2 * q))
            bar = rounded(120, 22, 11, (169, 184, 204), shadow=False)
            place(f, bar, CX + 40, cy - 150 + k * 100, clamp(q * 1.5) * out * 0.7)
    brackets(f, CX, cy, 640, S_FREE, t, out=out)
    if t > T("لمست") - 0.1:
        q = pop(t, T("لمست") - 0.1)
        place(f, pill("بدون ولا لمسة منك", 46, col=CYAN), CX, 300, clamp(q * 1.5) * out, 0.8 + 0.2 * q)

def scene_web(f, t):
    if t < S_WEB - 0.1 or t > S_SEND + 0.1: return
    out = 1 - prog(t, S_SEND - 0.3, 0.25)
    p = ease_out(prog(t, S_WEB, 0.4)); a = p * out
    bar = rounded(840, 110, 55, DNAVY, border=(0, 212, 255, 180), shadow=False).copy()
    q = "تيشيرتات قطن قريب مني"
    nchar = int(clamp((t - S_WEB - 0.2) / 1.3) * len(q))
    if nchar:
        tx = text_img(q[:nchar], AR, 44, WHITE)
        bar.alpha_composite(tx, (bar.width - 90 - tx.width + 40, (bar.height - tx.height) // 2))
    dd = ImageDraw.Draw(bar)
    dd.ellipse((70, 38, 110, 78), outline=CYAN + (255,), width=6); dd.line((104, 72, 122, 90), fill=CYAN + (255,), width=6)
    place(f, bar, CX, 300, a)
    place(f, text_img("Google", EN, 56, GRAY, rtl=False), CX, 195, a * 0.9)
    st = SEG[21][0] - 0.1
    if t > st - 0.1:
        q2 = ease_back(prog(t, st, 0.45))
        place(f, site_card(2), CX, 900, clamp(q2 * 1.5) * out, 0.7 + 0.15 * q2)
    else:
        lay, d = overlay(f)
        for k in range(3):
            y = 470 + k * 150; al = int(120 * a * prog(t, S_WEB + 0.5 + k * 0.2, 0.3))
            d.rounded_rectangle((150, y, 930, y + 110), 30, fill=(14, 30, 58, al))
            d.rounded_rectangle((420, y + 30, 880, y + 50), 10, fill=GRAY + (al,))
            d.rounded_rectangle((560, y + 66, 880, y + 82), 8, fill=GRAY + (al // 2,))
        f.alpha_composite(lay)

def scene_send(f, t):
    if t < S_SEND - 0.1 or t > T_OUT + 0.4: return
    out = 1 - prog(t, T_OUT, 0.3)
    p = ease_back(prog(t, S_SEND, 0.45))
    k = t - S_SEND
    x = CX + math.sin(k * 2.2) * 110; y = 860 - k * 40
    s = 150 * (0.6 + 0.4 * p)
    lay, d = overlay(f); al = int(255 * clamp(p * 1.5) * out)
    pts = [(x + s, y - s * 0.3), (x - s, y - s * 0.05), (x - s * 0.35, y + s * 0.15), (x - s * 0.2, y + s * 0.7)]
    d.polygon([pts[0], pts[1], pts[2]], fill=WHITE + (al,)); d.polygon([pts[0], pts[2], pts[3]], fill=CYAN + (al,))
    for j in range(4):
        tx = x - s - 40 - j * 50; ty = y + 20 + j * 18
        d.ellipse((tx - 8, ty - 8, tx + 8, ty + 8), fill=CYAN + (int(al * (1 - j / 4)),))
    f.alpha_composite(lay)
    place(f, pill("دزّه لصاحب محل تعرفه", 50), CX, 1180, ease_out(prog(t, T("لصاحب"), 0.3)) * out)

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
    ws = [("زبونك", False, T_OUT + 0.9), ("يسأل…", False, T_OUT + 1.2), ("والبوت", True, T_OUT + 1.5), ("يكمّل", True, T_OUT + 1.8)]
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
    scene_hook(f, t); scene_steps(f, t); scene_free(f, t); scene_web(f, t); scene_send(f, t)
    scene_outro(f, t)
    if t < T_OUT: captions(f, t)
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]: frame(int(round(float(ts) * FPS))).save(f"p_{ts}.png")
        sys.exit()
    out = os.environ.get("OUT", "v4.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out],
                         stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
