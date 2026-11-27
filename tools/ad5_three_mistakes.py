"""Reel 5 — concept 4: 3 أخطاء تخسّرك زبائن (three mistake cards, each one flips to its fix).
Usage: python3 ad5_three_mistakes.py [t1 t2 ...]  (preview frames) | no args -> v5.mp4 (OUT env)"""
import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from functools import lru_cache
from PIL import Image, ImageDraw
from style_ad import (background, brackets, word_img, blurred, site_card, bot_icon, bot_eyes, chat_icon,
                      gradient, text_img, rounded, place, ease_out, ease_back, prog, clamp,
                      NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, EN, EN_SB, W, H, FPS)
from render import AR_BLACK, AR_REG
from ad4_step_chat import pill, cust_bubble, bot_bubble, dot_img, overlay, pop

DUR = 44.0
N = int(DUR * FPS)
CX = W // 2
TY = 1530                      # caption centre
VY = 900                       # main visual centre
DIM = (110, 122, 140)

SEG = [(0.0, 1.43), (1.89, 3.74), (3.94, 5.65), (6.20, 6.98), (7.35, 8.30), (8.70, 9.63), (9.87, 10.81),
       (10.91, 11.91), (12.36, 12.81), (13.15, 14.97), (15.23, 17.04), (17.57, 18.39), (18.76, 20.35),
       (20.59, 21.38), (21.90, 22.36), (22.68, 25.48), (26.04, 26.90), (27.25, 28.47), (28.67, 30.15),
       (30.69, 31.13), (31.44, 33.52), (33.70, 37.00), (37.38, 39.42), (39.55, 40.46)]
TEXT = [["هلا بيك،", "صاحب محل؟"], ["خلّي أگلك", "ثلاث أخطاء صغيرة،"], ["بس تخسّرك", "زبائن كل يوم."],
        ["الغلطة الأولى:"], ["تتأخر بالرد."], ["الزبون يسأل،"], ["ينتظر شوية،"], ["ويروح لمحل ثاني."],
        ["الحل:"], ["موظف مبيعات ذكي", "من نيكسو،"], ["يرد بثانية", "وبكل لطف."],
        ["الغلطة الثانية:"], ["تعيد نفس الجواب", "كل يوم،"], ["لحد ما تتعب."], ["الحل:"],
        ["البوت يحفظ أسئلة زبائنك", "ويجاوبها بدالك."], ["الغلطة الثالثة:"], ["محلك يسكّر بالليل،"],
        ["والرسائل تبقى", "بدون رد."], ["الحل:"], ["البوت يشتغل", "أربعة وعشرين ساعة،"],
        ["ونسوّيلك موقع احترافي", "يلگاك بيه الزبون من گوگل."], ["دزّ هذا الفيديو", "لصاحب محل تعرفه،"], ["وراسلنا هسه."]]
ACCENT = {"محل؟", "ثلاث", "أخطاء", "زبائن", "الأولى:", "بالرد.", "ثاني.", "الحل:", "موظف", "مبيعات", "ذكي", "نيكسو،",
          "بثانية", "لطف.", "الثانية:", "الجواب", "تتعب.", "يحفظ", "بدالك.", "الثالثة:", "بالليل،", "رد.",
          "وعشرين", "ساعة،", "احترافي", "گوگل.", "دزّ", "تعرفه،", "هسه."}
VO_END = 40.46
T_OUT = 39.45

LINE_T = []   # each display line: [start, end, [(word, accent, t)]]; lines of one segment show together
for (s, e), lines in zip(SEG, TEXT):
    allw = [w for ln in lines for w in ln.split()]
    tot = sum(len(w) + 1 for w in allw); acc = 0; rows = []
    for ln in lines:
        row = []
        for w in ln.split():
            row.append((w, w in ACCENT, s + (e - s) * acc / tot)); acc += len(w) + 1
        rows.append(row)
    LINE_T.append([s, None, rows])
for i, L in enumerate(LINE_T):
    L[1] = (LINE_T[i + 1][0] - 0.03) if i + 1 < len(LINE_T) else VO_END
    if i + 1 < len(LINE_T) and LINE_T[i + 1][0] - L[0] > 4.2: L[1] = L[0] + 4.0

def T(word, after=0.0):
    for s, e, rows in LINE_T:
        for row in rows:
            for w, a, t in row:
                if w == word and t >= after: return t
    raise KeyError(word)

M1, F1, M2, F2, M3, F3, S_SEND = SEG[3][0], SEG[8][0], SEG[11][0], SEG[14][0], SEG[16][0], SEG[19][0], SEG[22][0]
S_WEB = SEG[21][0]
BLOCKS = [(M1, F1, F1, M2), (M2, F2, F2, M3), (M3, F3, F3, S_SEND)]

def captions(f, t, y=TY):
    for s, e, rows in LINE_T:
        if t < s - 0.06 or t > e or s >= T_OUT: continue
        out = 1 - prog(t, e - 0.18, 0.18)
        size = 92 if len(rows) == 1 else 84
        ys = [y] if len(rows) == 1 else [y - 58, y + 58]
        for row, yy in zip(rows, ys):
            imgs = [word_img(w, a, size) for w, a, _ in row]
            gap = -40; total = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
            sc = min(1.0, 990 / max(total, 1)); x = W / 2 + total * sc / 2
            for (w, a, st), im in zip(row, imgs):
                if t >= st - 0.06 or st < 0.05:
                    p = 1.0 if st < 0.05 else ease_out(prog(t, st - 0.06, 0.22))
                    place(f, im, x - im.width * sc / 2, yy + (1 - p) * 24, p * out, sc * (1.08 - 0.08 * p))
                x -= (im.width + gap) * sc

# ---------- shared pieces ----------
@lru_cache(None)
def x_mark(s=120, col=(255, 255, 255)):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s // 2; r = s * 0.42
    d.ellipse((c - r, c - r, c + r, c + r), fill=(40, 52, 78, 255), outline=DIM + (255,), width=5)
    k = r * 0.45
    d.line((c - k, c - k, c + k, c + k), fill=col + (255,), width=int(s * 0.09))
    d.line((c - k, c + k, c + k, c - k), fill=col + (255,), width=int(s * 0.09))
    return im

@lru_cache(None)
def big_num(n, fixed):
    """Huge outlined numeral for the block header."""
    col = CYAN if fixed else WHITE
    return text_img(str(n), EN, 230, col, rtl=False, glow=12 if fixed else 0)

def score(f, t, a):
    """Three small chips at the top: grey ✗ until each fix lands, then a cyan ✓."""
    if a <= 0.01: return
    xs = [CX + 150 - k * 150 for k in range(3)]
    for k, x in enumerate(xs):
        fixed = t >= BLOCKS[k][1] + 0.2
        active = BLOCKS[k][0] - 0.05 <= t < BLOCKS[k][3]
        im = dot_img("done") if fixed else x_mark(84)
        q = pop(t, BLOCKS[k][1] + 0.2) if fixed else 1
        sc = (1.0 + 0.1 * math.sin(t * 5)) if active and not fixed else 1.0
        place(f, im, x, 150, a, sc * (0.8 + 0.2 * q))

def header(f, t, k, s, fx, e):
    """'الغلطة N' header -> flips to 'الحل' at fx."""
    if t < s - 0.1 or t > e + 0.05: return
    out = 1 - prog(t, e - 0.3, 0.25)
    flip = prog(t, fx - 0.1, 0.3)
    p = ease_out(prog(t, s - 0.05, 0.35))
    sq = abs(math.cos(flip * math.pi))         # card-flip squash
    lab = ["الأولى", "الثانية", "الثالثة"][k]
    if flip < 0.5:
        num = big_num(k + 1, False); tt = text_img("الغلطة " + lab, AR_BLACK, 78, WHITE)
    else:
        num = big_num(k + 1, True); tt = text_img("الحل", AR_BLACK, 86, CYAN, glow=10)
    a = p * out
    if a <= 0.01: return
    n2 = num.resize((max(1, int(num.width * max(sq, 0.02))), num.height))
    place(f, n2, CX + 300, 330, a * 0.9)
    t2 = tt.resize((max(1, int(tt.width * max(sq, 0.02))), tt.height))
    place(f, t2, CX - 80 + (1 - p) * 60, 330, a)

# ---------- hook ----------
@lru_cache(None)
def mini_card(n):
    w, h = 300, 380
    c = rounded(w, h, 40, DNAVY, border=(169, 184, 204, 150), shadow=True).copy(); o = 40
    nt = text_img(str(n), EN, 150, WHITE, rtl=False)
    c.alpha_composite(nt, (o + (w - nt.width + 80) // 2 - 40, o + 40 - 20))
    xm = x_mark(110)
    c.alpha_composite(xm, (o + w // 2 - 55, o + h - 150))
    return c

def scene_hook(f, t):
    if t > M1 + 0.1: return
    out = 1 - prog(t, M1 - 0.4, 0.3)
    place(f, text_img("3 أخطاء", AR_BLACK, 150, WHITE), CX, 300, out)
    place(f, text_img("تخسّرك زبائن", AR_BLACK, 116, CYAN, glow=10), CX, 470, out)
    # three fanned cards (fully visible at frame 0)
    spread = 1 + 0.08 * ease_out(prog(t, SEG[1][0], 0.5))
    for k, ang in enumerate([12, 0, -12]):
        c = mini_card(3 - k)
        wob = math.sin(t * 2 + k) * 2
        r = c.rotate(ang + wob, expand=True, resample=Image.BICUBIC)
        lit = 1.0 if t < T("ثلاث") else 1.0
        place(f, r, CX + (k - 1) * 175 * spread, 950 + abs(k - 1) * 30, out * lit, 0.8)
    brackets(f, CX, 950, 680, -1.0, t, out=out)
    if t > SEG[2][0] - 0.1:
        q = pop(t, SEG[2][0] - 0.1)
        place(f, pill("كل يوم… بدون ما تحس", 44, col=CYAN), CX, 1360, clamp(q * 1.5) * out, 0.8 + 0.2 * q)

# ---------- mistake 1: slow reply ----------
def scene_b1(f, t):
    s, fx, _, e = BLOCKS[0]
    if t < s - 0.3 or t > e + 0.1: return
    out = 1 - prog(t, e - 0.3, 0.25)
    if t < fx + 0.05:
        a = ease_out(prog(t, s, 0.35)) * (1 - prog(t, fx - 0.2, 0.25))
        # customer message + "seen" waiting clock
        msgq = pop(t, SEG[5][0] - 0.1)
        place(f, cust_bubble("متوفر بلون ثاني؟", 50), CX + 140, 640, clamp(msgq * 1.5) * a, 0.85 + 0.15 * msgq)
        # clock face with sweeping hand (illustrative wait)
        cy = 920; R = 150
        lay, d = overlay(f); A = int(255 * a)
        d.ellipse((CX - R, cy - R, CX + R, cy + R), fill=DNAVY + (A,), outline=(169, 184, 204, A), width=8)
        sweep = clamp((t - SEG[4][0]) / 4.0)
        if sweep > 0:
            d.pieslice((CX - R + 14, cy - R + 14, CX + R - 14, cy + R - 14), -90, -90 + 360 * sweep, fill=(0, 102, 255, int(110 * a)))
        ang = -math.pi / 2 + 2 * math.pi * sweep * 1.0
        d.line((CX, cy, CX + math.cos(ang) * (R - 34), cy + math.sin(ang) * (R - 34)), fill=WHITE + (A,), width=10)
        d.ellipse((CX - 14, cy - 14, CX + 14, cy + 14), fill=CYAN + (A,))
        f.alpha_composite(lay)
        place(f, text_img("بانتظار الرد…", AR, 44, GRAY), CX, 1130, a * ease_out(prog(t, SEG[4][0] + 0.2, 0.3)))
        # customer leaves: avatar slides away with arrow
        if t > SEG[7][0] - 0.1:
            q = ease_out(prog(t, SEG[7][0] - 0.1, 0.7))
            lay, d = overlay(f); A = int(255 * a)
            ax = CX + 330 - q * 650; ay = 920
            d.ellipse((ax - 40, ay - 120, ax + 40, ay - 40), fill=GRAY + (A,))
            d.rounded_rectangle((ax - 62, ay - 30, ax + 62, ay + 90), 50, fill=GRAY + (A,))
            f.alpha_composite(lay)
            place(f, pill("راح لمحل ثاني", 40, border=(169, 184, 204, 140), col=GRAY), CX, 1240, clamp(q * 1.6) * a)
    else:
        a = ease_out(prog(t, fx, 0.35)) * out
        place(f, cust_bubble("متوفر بلون ثاني؟", 50), CX + 140, 620, a)
        if t < SEG[10][0]:
            from ad4_step_chat import typing
            typing(f, CX - 250, 770, t, a * prog(t, fx + 0.2, 0.2))
        q = pop(t, SEG[10][0] - 0.05)
        place(f, bot_bubble("إي متوفر بالأزرق والأسود", 46), CX - 120, 770, clamp(q * 1.5) * out, 0.85 + 0.15 * q)
        bq = ease_back(prog(t, fx + 0.1, 0.5))
        place(f, bot_icon(), CX, 1060, clamp(bq * 1.4) * out, 0.48 * (0.7 + 0.3 * bq))
        bot_eyes(f, CX, 1060, 0.48 * (0.7 + 0.3 * bq), t, clamp(bq * 1.4) * out)
        if t > T("بثانية") - 0.15:
            q2 = pop(t, T("بثانية") - 0.15)
            place(f, pill("رد خلال ثانية", 46, col=CYAN), CX, 1290, clamp(q2 * 1.5) * out, 0.8 + 0.2 * q2)

# ---------- mistake 2: same answer every day ----------
REP = "عدكم توصيل للمحافظات؟"
def scene_b2(f, t):
    s, fx, _, e = BLOCKS[1]
    if t < s - 0.3 or t > e + 0.1: return
    out = 1 - prog(t, e - 0.3, 0.25)
    if t < fx + 0.05:
        a = ease_out(prog(t, s, 0.3)) * (1 - prog(t, fx - 0.2, 0.25))
        # the same question piling up, slightly rotated each time
        for k in range(6):
            st = SEG[12][0] - 0.3 + k * 0.42
            q = pop(t, st, 0.3)
            if q <= 0.01: continue
            b = cust_bubble(REP, 46)
            r = b.rotate((k % 3 - 1) * 4, expand=True, resample=Image.BICUBIC)
            place(f, r, CX + ((k % 2) * 2 - 1) * 60, 560 + k * 105, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
        if t > SEG[13][0] - 0.1:
            q = pop(t, SEG[13][0] - 0.1)
            place(f, pill("نفس السؤال… مرة ثانية وثالثة", 42, border=(169, 184, 204, 140), col=GRAY), CX, 1250,
                  clamp(q * 1.5) * a, 0.8 + 0.2 * q)
    else:
        a = ease_out(prog(t, fx, 0.35)) * out
        # FAQ card: questions answered one by one
        w, h = 900, 640
        place(f, faq_card(nfaq(t)), CX, 860, a, 0.94 + 0.06 * a)

def nfaq(t):
    st = SEG[15][0]
    return min(4, max(0, int((t - st) / 0.6) + 1)) if t > st else 0

@lru_cache(None)
def faq_card(n):
    w, h = 900, 660
    c = rounded(w, h, 50, DNAVY, border=(0, 212, 255, 160)).copy(); d = ImageDraw.Draw(c); o = 40
    d.rounded_rectangle((o, o, o + w, o + 120), 50, fill=(12, 30, 62, 255)); d.rectangle((o, o + 70, o + w, o + 120), fill=(12, 30, 62, 255))
    d.line((o, o + 120, o + w, o + 120), fill=(0, 212, 255, 90), width=3)
    hd = text_img("أسئلة زبائنك المتكررة", AR, 44, WHITE)
    c.alpha_composite(hd, (o + w - 50 - hd.width + 40, o + 60 - hd.height // 2))
    ic = bot_icon().resize((96, 96))
    c.alpha_composite(ic, (o + 30, o + 12))
    QA = [("عدكم توصيل؟", "إي، لكل المحافظات"), ("وين موقعكم؟", "يدزّ اللوكيشن فوراً"),
          ("أكو قياسات؟", "يعرض كل القياسات"), ("شلون أطلب؟", "يثبّت الطلب بنفسه")]
    for k, (q, ans) in enumerate(QA):
        y = o + 185 + k * 122
        done = k < n
        qt = text_img(q, AR, 40, WHITE if done else GRAY)
        c.alpha_composite(qt, (o + w - 130 - qt.width + 40, y - qt.height // 2))
        mk = dot_img("done") if done else dot_img("todo", k + 1)
        c.alpha_composite(mk, (o + w - 70 - mk.width // 2, y - mk.height // 2))
        if done:
            at = text_img(ans, AR_REG, 34, CYAN)
            c.alpha_composite(at, (o + 40, y - at.height // 2))
        if k < 3: d.line((o + 50, y + 61, o + w - 50, y + 61), fill=(169, 184, 204, 50), width=2)
    return c

# ---------- mistake 3: shop closes at night ----------
def scene_b3(f, t):
    s, fx, _, e = BLOCKS[2]
    if t < s - 0.3 or t > e + 0.1: return
    out = 1 - prog(t, e - 0.3, 0.25)
    if t < fx + 0.05:
        a = ease_out(prog(t, s, 0.3)) * (1 - prog(t, fx - 0.2, 0.25))
        # moon
        lay, d = overlay(f); A = int(235 * a)
        mx, my, r = CX + 330, 560, 60
        d.ellipse((mx - r, my - r, mx + r, my + r), fill=WHITE + (A,))
        d.ellipse((mx - r * 0.4, my - r * 1.2, mx + r * 1.4, my + r * 0.5), fill=NAVY + (255 if a > 0.98 else A,))
        f.alpha_composite(lay)
        # shop front with a shutter rolling down
        place(f, shop_front(), CX, 860, a)
        sh = ease_out(prog(t, SEG[17][0] + 0.2, 1.0))
        if sh > 0:
            lay, d = overlay(f); A = int(255 * a)
            x0, x1, y0 = CX - 250, CX + 250, 780
            yb = y0 + 300 * sh
            d.rectangle((x0, y0, x1, yb), fill=(70, 84, 110, A))
            for yy in range(int(y0 + 18), int(yb), 26): d.line((x0, yy, x1, yy), fill=(45, 56, 80, A), width=4)
            f.alpha_composite(lay)
        if t > T("بالليل،"):
            q = pop(t, T("بالليل،"))
            place(f, pill("مسكّر", 46, border=(169, 184, 204, 160), col=WHITE), CX, 960, clamp(q * 1.5) * a, 0.8 + 0.2 * q)
        # unanswered messages piling up beside the shop
        for k in range(3):
            st = SEG[18][0] + k * 0.35
            q = pop(t, st, 0.3)
            if q > 0.01:
                place(f, pill("رسالة بدون رد", 38, border=(169, 184, 204, 120), col=GRAY), CX + (k - 1) * 40, 1200 + k * 72,
                      clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    else:
        a = ease_out(prog(t, fx, 0.35)) * out
        if t < S_WEB - 0.05:
            # 24/7 ring filling
            o2 = 1 - prog(t, S_WEB - 0.35, 0.3)
            cy = 880; R = 260
            fill = ease_out(prog(t, SEG[20][0], 1.8))
            lay, d = overlay(f); A = int(255 * a * o2)
            d.ellipse((CX - R, cy - R, CX + R, cy + R), outline=(40, 60, 95, A), width=26)
            if fill > 0: d.arc((CX - R, cy - R, CX + R, cy + R), -90, -90 + 360 * fill, fill=CYAN + (A,), width=26)
            ang = -math.pi / 2 + 2 * math.pi * fill
            d.ellipse((CX + math.cos(ang) * R - 24, cy + math.sin(ang) * R - 24, CX + math.cos(ang) * R + 24, cy + math.sin(ang) * R + 24), fill=WHITE + (A,))
            f.alpha_composite(lay)
            place(f, text_img("24", EN, 190, WHITE, rtl=False), CX, cy - 30, a * o2)
            place(f, text_img("ساعة", AR, 64, CYAN), CX, cy + 105, a * o2)
            # small moon + sun swapping on the ring
            q = pop(t, T("ساعة،") - 0.1)
            place(f, pill("حتى وإنت نايم", 44, col=CYAN), CX, 1250, clamp(q * 1.5) * a * o2, 0.8 + 0.2 * q)
        else:
            # Google search bar + website card
            p = ease_out(prog(t, S_WEB, 0.4)); aa = p * out
            bar = rounded(840, 110, 55, DNAVY, border=(0, 212, 255, 180), shadow=False).copy()
            qtxt = "محل ملابس قريب مني"
            nchar = int(clamp((t - S_WEB - 0.2) / 1.2) * len(qtxt))
            if nchar:
                tx = text_img(qtxt[:nchar], AR, 44, WHITE)
                bar.alpha_composite(tx, (bar.width - 90 - tx.width + 40, (bar.height - tx.height) // 2))
            dd = ImageDraw.Draw(bar)
            dd.ellipse((70, 38, 110, 78), outline=CYAN + (255,), width=6); dd.line((104, 72, 122, 90), fill=CYAN + (255,), width=6)
            place(f, text_img("Google", EN, 56, GRAY, rtl=False), CX, 520, aa * 0.9)
            place(f, bar, CX, 625, aa)
            st = T("احترافي") - 0.1
            q2 = ease_back(prog(t, st, 0.45))
            if q2 > 0.01:
                place(f, site_card(1), CX, 1035, clamp(q2 * 1.5) * out, 0.58 + 0.12 * q2)

@lru_cache(None)
def shop_front():
    w, h = 560, 420
    im = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im); o = 40
    # awning
    for k in range(7):
        col = BLUE if k % 2 == 0 else CYAN
        d.polygon([(o + k * 80, o), (o + (k + 1) * 80, o), (o + (k + 1) * 80, o + 70), (o + k * 80, o + 70)], fill=col + (255,))
        d.pieslice((o + k * 80, o + 30, o + (k + 1) * 80, o + 110), 0, 180, fill=col + (255,))
    d.rectangle((o + 30, o + 100, o + w - 30, o + h), fill=DNAVY + (255,), outline=(169, 184, 204, 200), width=5)
    d.rectangle((o + 30, o + h - 8, o + w - 30, o + h), fill=(169, 184, 204, 255))
    return im

# ---------- send + outro ----------
def scene_send(f, t):
    if t < S_SEND - 0.1 or t > T_OUT + 0.4: return
    out = 1 - prog(t, T_OUT, 0.3)
    p = ease_back(prog(t, S_SEND, 0.45))
    k = t - S_SEND
    x = CX - 120 + k * 120; y = 880 - math.sin(k * 2.0) * 60
    s = 150 * (0.6 + 0.4 * p)
    lay, d = overlay(f); al = int(255 * clamp(p * 1.5) * out)
    pts = [(x + s, y - s * 0.3), (x - s, y - s * 0.05), (x - s * 0.35, y + s * 0.15), (x - s * 0.2, y + s * 0.7)]
    d.polygon([pts[0], pts[1], pts[2]], fill=WHITE + (al,)); d.polygon([pts[0], pts[2], pts[3]], fill=CYAN + (al,))
    for j in range(4):
        tx = x - s - 40 - j * 50; ty = y + 20 + j * 18
        d.ellipse((tx - 8, ty - 8, tx + 8, ty + 8), fill=CYAN + (int(al * (1 - j / 4)),))
    f.alpha_composite(lay)
    place(f, pill("دزّه لصاحب محل تعرفه", 50), CX, 1200, ease_out(prog(t, T("لصاحب"), 0.3)) * out)

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
    ws = [("صلّح", True, T_OUT + 0.9), ("الأخطاء…", False, T_OUT + 1.2), ("وخلّي", False, T_OUT + 1.5), ("الزبون", False, T_OUT + 1.8), ("يرجع", True, T_OUT + 2.1)]
    imgs = [word_img(w, a) for w, a, _ in ws]; gap = -40
    total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    sc = min(1.0, 960 / total); x = W / 2 + total * sc / 2
    for (w, a, st), im in zip(ws, imgs):
        r = ease_out(prog(t, st, 0.26))
        if r > 0.01: place(f, blurred(w, a, int(round((1 - r) * 8))), x - im.width * sc / 2, 1040 + (1 - r) * 24, r, sc)
        x -= (im.width + gap) * sc
    c = ease_back(prog(t, T_OUT + 2.4, 0.45))
    if c > 0.01:
        btn = rounded(640, 140, 70, BLUE, grad=(BLUE, (0, 160, 255))).copy()
        bt = text_img("راسلنا هسه", AR, 70, WHITE)
        btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
        pulse = 1 + 0.035 * math.sin(t * 6) * prog(t, T_OUT + 2.9, 0.3)
        place(f, btn, CX, 1300, clamp(c * 1.4), (0.8 + 0.2 * c) * pulse)
    dd = ease_out(prog(t, T_OUT + 2.8, 0.4))
    place(f, text_img("WhatsApp  07751027553", EN_SB, 50, WHITE, rtl=False), CX, 1490, dd)
    place(f, text_img("nexodeveloper.net", EN_SB, 46, CYAN, rtl=False), CX, 1570, dd)
    place(f, text_img("Connect to the Future.", EN_SB, 40, GRAY, rtl=False), CX, 1680, ease_out(prog(t, T_OUT + 3.3, 0.5)))

def frame(i):
    t = i / FPS
    f = background(t)
    scene_hook(f, t); scene_b1(f, t); scene_b2(f, t); scene_b3(f, t); scene_send(f, t); scene_outro(f, t)
    if M1 - 0.3 < t < S_SEND:
        sa = ease_out(prog(t, M1 - 0.3, 0.4)) * (1 - prog(t, S_SEND - 0.3, 0.3))
        score(f, t, sa)
        for k, (s, fx, _, e) in enumerate(BLOCKS): header(f, t, k, s, fx, e)
    if t < T_OUT: captions(f, t)
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]: frame(int(round(float(ts) * FPS))).save(f"p_{ts}.png")
        sys.exit()
    out = os.environ.get("OUT", "v5.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out],
                         stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
