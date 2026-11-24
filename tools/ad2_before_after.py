import sys, os, math, re, json, subprocess
sys.path.insert(0, "/home/claude/nexo/tools")
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from style_ad import (background, brackets, word_img, blurred, chat_icon, site_card, bot_icon, bot_eyes,
                      gradient, text_img, rounded, place, ease_out, ease_back, prog, clamp,
                      NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, EN, EN_SB, W, H, FPS)

DUR = 50.0
N = int(DUR * FPS)
CX, CY, TY = W // 2, 860, 1400
DIM = (110, 122, 140)

# ---------- word timing from speech intervals ----------
SCRIPT = ("صاحب محل؟ | هذا الفيديو إلك… | خلّينا نشوف يومين من حياة محلك. || قبل: | رسائل تتجمّع بالماسنجر والإنستا… | "
          "زبون يسأل عن السعر وينتظر… | ساعة، ساعتين… | وبالأخير يكتب: | خلاص، اشتريت من غيرك. || بعد نيكسو: | نفس الرسالة… | "
          "بس هالمرة | موظف مبيعات ذكي يرد بثانية. | يجاوب على سؤاله، | يعرضله المنتجات، | ويثبّت الطلب… | حتى لو جانت الساعة | ثنتين بالليل. || "
          "والزبون اللي يدوّر عليك بالإنترنت؟ | يلگى موقع احترافي | يخلّي محلك مفتوح | أربعة وعشرين ساعة. || الفرق؟ | قبل جنت تخسر زبائن | "
          "وإنت ما تدري… | هسه تكسبهم | وإنت مرتاح. || دزّ هذا الفيديو | لصاحب محل تعرفه… | وراسلنا هسه. | نيكسو.")
ACCENT = {"محل؟", "إلك…", "يومين", "قبل:", "غيرك.", "بعد", "نيكسو:", "موظف", "مبيعات", "ذكي", "بثانية.", "ويثبّت", "الطلب…",
          "ثنتين", "بالليل.", "احترافي", "مفتوح", "ساعة.", "الفرق؟", "تخسر", "تكسبهم", "مرتاح.", "دزّ", "تعرفه…", "هسه.", "نيكسو."}
SIL = json.load(open("/home/claude/v2/sil.json"))   # list of [start, end] silences
VO_END = 43.68

def speech_intervals():
    iv, t = [], 0.0
    for s, e in SIL:
        if s > t: iv.append((t, s))
        t = e
    if t < VO_END: iv.append((t, VO_END))
    return iv
IV = speech_intervals()
TOTAL = sum(e - s for s, e in IV)
def at_fraction(fr):
    target = fr * TOTAL
    for s, e in IV:
        d = e - s
        if target <= d: return s + target
        target -= d
    return VO_END

phrases = [p.strip() for p in SCRIPT.replace("||", "|").split("|") if p.strip()]
words = [w for p in phrases for w in p.split()]
weights = [len(w) + 1 for w in words]
cum, acc = [], 0
for wt in weights: cum.append(acc); acc += wt
# rough times, then snap section starts to real pauses and redistribute inside sections
rough = [at_fraction(c / acc) for c in cum]
ANCH = ["قبل:", "بعد", "والزبون", "الفرق؟", "دزّ"]
ends = [e for s_, e in SIL if e - s_ >= 0.25]
idx = [0]; tim = [0.0]
for aw in ANCH:
    i = words.index(aw); r = rough[i]
    cand = [e for e in ends if r - 0.6 <= e <= r + 2.0]
    tt = min(cand, key=lambda e: abs(e - (r + 0.9))) if cand else r
    idx.append(i); tim.append(tt)
idx.append(len(words)); tim.append(VO_END)
def speech_between(a, b):
    return [(max(s_, a), min(e, b)) for s_, e in IV if min(e, b) > max(s_, a)]
times = [0.0] * len(words)
for j in range(len(idx) - 1):
    i0, i1, a, b = idx[j], idx[j + 1], tim[j], tim[j + 1]
    ivs = speech_between(a, b); tot = sum(e - s_ for s_, e in ivs) or 1
    wsum = sum(weights[i0:i1]); c = 0
    for i in range(i0, i1):
        target = c / wsum * tot; t0 = a
        for s_, e in ivs:
            if target <= e - s_: t0 = s_ + target; break
            target -= e - s_
        times[i] = t0; c += weights[i]
LINES = []
k = 0
for p in phrases:
    ws = p.split(); row = []
    for w in ws:
        row.append((w, w in ACCENT, times[k])); k += 1
    LINES.append(row)
# line end = next line start
LINE_T = []
for i, row in enumerate(LINES):
    s = row[0][2]
    e = LINES[i + 1][0][2] - 0.05 if i + 1 < len(LINES) else VO_END + 0.3
    LINE_T.append((s, e, row))
def T(word):   # first time a word starts
    for row in LINES:
        for w, a, t in row:
            if w == word: return t
    raise KeyError(word)

T_BEFORE, T_AFTER = T("قبل:"), T("بعد")
T_WEB, T_DIFF, T_SEND = T("والزبون"), T("الفرق؟"), T("دزّ")
T_HOURS, T_FINAL, T_NIGHT = T("ساعة،"), T("خلاص،"), T("حتى")
T_BOT, T_ANS, T_SHOW, T_ORDER = T("موظف"), T("يجاوب"), T("يعرضله"), T("ويثبّت")
T_SITE, T_OPEN, T_GAIN = T("يلگى"), T("يخلّي"), T("هسه")
T_OUT = VO_END - 0.2

def captions(f, t, y=TY):
    for s, e, ws in LINE_T:
        if t < s - 0.01 or t > e + 0.25: continue
        out = 1 - prog(t, e, 0.2)
        imgs = [word_img(w, a) for w, a, _ in ws]
        gap = -40; total = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
        sc = min(1.0, 980 / max(total, 1)); x = W / 2 + total * sc / 2
        for (w, a, st), im in zip(ws, imgs):
            if t >= st:
                p = ease_out(prog(t, st, 0.24))
                place(f, blurred(w, a, int(round((1 - p) * 8))), x - im.width * sc / 2, y + (1 - p) * 24, p * out, sc * (1.08 - 0.08 * p))
            x -= (im.width + gap) * sc

def overlay(f):
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)

def pill(txt, size=42, border=(0, 212, 255, 220), fill=DNAVY, col=WHITE, font=AR, rtl=True):
    tx = text_img(txt, font, size, col, rtl=rtl)
    p = rounded(tx.width - 80 + 70, size + 50, (size + 50) // 2, fill, border=border, shadow=False).copy()
    p.alpha_composite(tx, ((p.width - tx.width) // 2, (p.height - tx.height) // 2))
    return p

def chip(txt, active):
    col = BLUE if active else (60, 70, 88)
    tx = text_img(txt, AR, 64, WHITE)
    c = rounded(tx.width - 80 + 110, 120, 60, col, grad=((BLUE, CYAN) if active else None), shadow=active).copy()
    c.alpha_composite(tx, ((c.width - tx.width) // 2, (c.height - tx.height) // 2))
    return c

@lru_cache(None)
def shop_icon():
    s = 460; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 190, 400, 420), 28, fill=WHITE + (255,))
    for k in range(6):  # awning stripes
        x0 = 40 + k * 63
        col = CYAN if k % 2 == 0 else WHITE
        d.pieslice((x0, 120, x0 + 63, 230), 0, 180, fill=col + (255,))
        d.rectangle((x0, 100, x0 + 63, 176), fill=col + (255,))
    d.rounded_rectangle((95, 255, 210, 420), 14, fill=NAVY + (255,))      # door
    d.rounded_rectangle((245, 255, 370, 345), 14, fill=(14, 40, 80, 255))  # window
    d.ellipse((185, 330, 197, 342), fill=CYAN + (255,))
    return im

def phone(w=640, h=880, dim=False):
    return rounded(w, h, 70, (12, 18, 30) if dim else DNAVY, border=((110, 122, 140, 90) if dim else (0, 212, 255, 120)))

def gray_bubble(txt, size=40):
    return pill(txt, size, border=(110, 122, 140, 110), fill=(18, 26, 40), col=(200, 206, 216))

def bot_bubble(txt, size=38):
    b = text_img(txt, AR, size, WHITE)
    bb = rounded(b.width - 80 + 60, size + 50, (size + 50) // 2, BLUE, grad=(BLUE, (0, 150, 255)), shadow=False).copy()
    bb.alpha_composite(b, ((bb.width - b.width) // 2, (bb.height - b.height) // 2))
    return bb

# ---------- scenes ----------
def scene_hook(f, t):
    if t > T_BEFORE + 0.1: return
    out = 1 - prog(t, T_BEFORE - 0.35, 0.3)
    p = ease_back(prog(t, 0.0, 0.6))
    place(f, shop_icon(), CX, CY - 30 + math.sin(t * 3) * 6, clamp(p * 1.4) * out, 0.6 + 0.4 * p)
    brackets(f, CX, CY - 20, 600, 0.2, t, out=out)
    lay, d = overlay(f)  # sparkles
    for k in range(10):
        ph = (t * 0.4 + k * 0.1) % 1
        x = CX + math.sin(k * 2.1) * 360; y = CY + 300 - ph * 600
        al = int(200 * out * math.sin(ph * math.pi))
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(CYAN if k % 2 else BLUE) + (al,))
    f.alpha_composite(lay)
    # two day chips preview at "يومين"
    tday = T("يومين")
    for i, (txt, act) in enumerate([("قبل", False), ("بعد", True)]):
        q = ease_back(prog(t, tday + i * 0.25, 0.4))
        if q > 0.01:
            place(f, chip(txt, act), CX + (1 - 2 * i) * 200, CY + 330, clamp(q * 1.5) * out, 0.7 + 0.3 * q)

def scene_before(f, t):
    if t < T_BEFORE - 0.2 or t > T_AFTER + 0.1: return
    out = 1 - prog(t, T_AFTER - 0.3, 0.25)
    pin = ease_out(prog(t, T_BEFORE - 0.1, 0.4)); a = pin * out
    place(f, chip("قبل", False), CX, 300, a)
    place(f, phone(dim=True), CX, CY + 60 + (1 - pin) * 150, a)
    top = CY + 60 - 440 + 60
    # clock top-left of phone, spinning at "ساعة، ساعتين"
    hrs = clamp((t - T_HOURS) / 1.6) * 2
    clock = f"{9 + int(hrs)}:{int((hrs % 1) * 60):02d} PM"
    place(f, text_img(clock, EN_SB, 44, DIM, rtl=False), CX + 180, top + 20, a)
    lay, d = overlay(f)
    cx_, cy_ = CX - 200, top + 22
    d.ellipse((cx_ - 30, cy_ - 30, cx_ + 30, cy_ + 30), outline=DIM + (int(255 * a),), width=5)
    ang = (t - T_BEFORE) * (6 if t > T_HOURS else 1.2)
    d.line((cx_, cy_, cx_ + 20 * math.sin(ang), cy_ - 20 * math.cos(ang)), fill=DIM + (int(255 * a),), width=5)
    d.line((cx_, cy_, cx_ + 13 * math.sin(ang / 12), cy_ - 13 * math.cos(ang / 12)), fill=DIM + (int(255 * a),), width=6)
    f.alpha_composite(lay)
    msgs = ["مرحبا، متوفر؟", "شكد السعر؟", "تكدرون توصلون؟", "؟؟", "أحد موجود؟"]
    t_first = T("رسائل")
    n = 0
    for i, m in enumerate(msgs):
        st = t_first + i * 0.5
        q = ease_back(prog(t, st, 0.3))
        if q > 0.01:
            n += 1
            b = gray_bubble(m)
            place(f, b, CX - 270 + b.width / 2, top + 120 + i * 105, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    if n:
        badge = rounded(110, 76, 38, (90, 100, 118), shadow=False).copy()
        num = text_img(str(n * 2 - 1 if n > 1 else 1), EN, 46, WHITE, rtl=False)
        badge.alpha_composite(num, ((badge.width - num.width) // 2, (badge.height - num.height) // 2))
        place(f, badge, CX + 250, top + 100, a)
    if t > T_FINAL - 0.2:
        q = ease_back(prog(t, T_FINAL, 0.35))
        b = gray_bubble("خلاص… اشتريت من غيرك", 42)
        place(f, b, CX - 270 + b.width / 2, top + 680, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    # dark veil = "missed"
    if a > 0.01:
        lay, d = overlay(f); d.rectangle((0, 0, W, H), fill=(0, 0, 0, int(50 * a))); f.alpha_composite(lay)

def wipe(f, t):
    p = prog(t, T_AFTER - 0.35, 0.55)
    if 0 < p < 1:
        x = W * (1 - ease_out(p))
        lay, d = overlay(f)
        d.rectangle((x, 0, W, H), fill=CYAN + (int(40 * (1 - p)),))
        d.line((x, 0, x, H), fill=CYAN + (230,), width=10)
        glow = lay.filter(ImageFilter.GaussianBlur(18))
        f.alpha_composite(glow); f.alpha_composite(lay)

def scene_after(f, t):
    if t < T_AFTER - 0.1 or t > T_WEB + 0.1: return
    out = 1 - prog(t, T_WEB - 0.3, 0.25)
    pin = ease_out(prog(t, T_AFTER, 0.35)); a = pin * out
    place(f, chip("بعد", True), CX, 300, a, 0.9 + 0.1 * ease_back(prog(t, T_AFTER, 0.4)))
    place(f, phone(), CX, CY + 60, a)
    top = CY + 60 - 440 + 60
    night = t > T_NIGHT - 0.1
    place(f, text_img("2:00 AM" if night else "9:00 PM", EN_SB, 44, GRAY, rtl=False), CX + 180, top + 20, a)
    lay, d = overlay(f)
    ix, iy = CX - 200, top + 22
    if night:
        d.ellipse((ix - 26, iy - 26, ix + 26, iy + 26), fill=WHITE + (int(230 * a),))
        d.ellipse((ix - 12, iy - 34, ix + 36, iy + 14), fill=DNAVY + (int(255 * a),))
    else:
        d.ellipse((ix - 14, iy - 14, ix + 14, iy + 14), fill=CYAN + (int(255 * a),))
    f.alpha_composite(lay)
    y = top + 120
    q = ease_back(prog(t, T_AFTER + 0.4, 0.3))
    if q > 0.01:
        b = gray_bubble("شكد السعر؟")
        place(f, b, CX - 270 + b.width / 2, y, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    # timer chip 00:01 at bot reply
    if t > T_BOT:
        q = ease_back(prog(t, T_BOT, 0.3))
        tc = pill("00:01", 40, font=EN, rtl=False, col=CYAN)
        place(f, tc, CX + 200, y + 90, clamp(q * 1.5) * a, 0.8 + 0.2 * q)
        bb = bot_bubble("هلا بيك! هذا السعر والتفاصيل")
        place(f, bb, max(CX - 290 + bb.width / 2 - 40, CX + 300 - bb.width / 2 + 40) if bb.width < 700 else CX, y + 190, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    if t > T_ANS:
        q = ease_back(prog(t, T_ANS, 0.3))
        bb = bot_bubble("إي نعم، التوصيل متوفر")
        place(f, bb, max(CX - 290 + bb.width / 2 - 40, CX + 300 - bb.width / 2 + 40) if bb.width < 700 else CX, y + 300, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
    if t > T_SHOW:
        for k in range(3):
            qq = ease_back(prog(t, T_SHOW + k * 0.15, 0.3))
            card = rounded(160, 150, 26, DNAVY, border=(0, 212, 255, 160), shadow=False).copy()
            g = gradient(130, 80, *[(BLUE, CYAN), (BLUE, PURPLE), (CYAN, PURPLE)][k]).convert("RGBA")
            mm = Image.new("L", g.size, 0); ImageDraw.Draw(mm).rounded_rectangle((0, 0, 130, 80), 16, fill=255)
            card.paste(g, (55, 55), mm)
            place(f, card, CX + 190 - k * 190, y + 450, clamp(qq * 1.5) * a, 0.8 + 0.2 * qq)
    if t > T_ORDER:
        q = ease_back(prog(t, T_ORDER, 0.35))
        bb = bot_bubble("تم تثبيت طلبك ✓", 42)
        place(f, bb, CX, y + 620, clamp(q * 1.5) * a, 0.8 + 0.2 * q)

def scene_web(f, t):
    if t < T_WEB - 0.1 or t > T_DIFF + 0.1: return
    out = 1 - prog(t, T_DIFF - 0.3, 0.25)
    # search bar typing
    p = ease_out(prog(t, T_WEB, 0.4)); a = p * out
    bar = rounded(820, 110, 55, DNAVY, border=(0, 212, 255, 180), shadow=False).copy()
    q = "محل قريب مني"
    nchar = int(clamp((t - T_WEB - 0.2) / 1.2) * len(q))
    if nchar:
        tx = text_img(q[:nchar], AR, 46, WHITE)
        bar.alpha_composite(tx, (bar.width - 90 - tx.width + 40, (bar.height - tx.height) // 2))
    dd = ImageDraw.Draw(bar)
    dd.ellipse((70, 38, 110, 78), outline=CYAN + (255,), width=6); dd.line((104, 72, 122, 90), fill=CYAN + (255,), width=6)
    place(f, bar, CX, 360, a)
    if t > T_SITE - 0.1:
        q2 = ease_back(prog(t, T_SITE, 0.45))
        place(f, site_card(0), CX, CY + 80, clamp(q2 * 1.5) * out, 0.6 + 0.2 * q2)
    if t > T_OPEN:
        q3 = ease_back(prog(t, T_OPEN, 0.4))
        sign = pill("مفتوح 24/7", 56, border=(0, 212, 255, 255), fill=NAVY, col=CYAN)
        flick = 0.85 + 0.15 * math.sin(t * 20) if t < T_OPEN + 0.5 else 1
        place(f, sign, CX + 230, CY - 230, clamp(q3 * 1.5) * out * flick, 0.7 + 0.3 * q3)

def scene_diff(f, t):
    if t < T_DIFF - 0.1 or t > T_SEND + 0.1: return
    out = 1 - prog(t, T_SEND - 0.3, 0.25)
    p = ease_out(prog(t, T_DIFF, 0.4))
    lay, d = overlay(f)
    # right half (RTL first) = before, left half = now
    d.rectangle((W / 2, 380, W, 1250), fill=(20, 26, 38, int(230 * p * out)))
    d.rectangle((0, 380, W / 2, 1250), fill=(4, 30, 70, int(230 * p * out)))
    d.line((W / 2, 380, W / 2, 1250), fill=CYAN + (int(255 * p * out),), width=6)
    f.alpha_composite(lay)
    place(f, text_img("قبل", AR, 70, DIM), W * 0.75, 470, p * out)
    place(f, text_img("هسه", AR, 70, CYAN), W * 0.25, 470, p * out)
    # arrows
    lay, d = overlay(f)
    qa = ease_out(prog(t, T("تخسر"), 0.5)); qb = ease_out(prog(t, T_GAIN, 0.5))
    x1, x2 = W * 0.75, W * 0.25
    if qa > 0:
        y0, y1 = 620, 620 + 420 * qa
        d.line((x1, y0, x1, y1), fill=DIM + (int(255 * out),), width=22)
        d.polygon([(x1 - 50, y1 - 10), (x1 + 50, y1 - 10), (x1, y1 + 60)], fill=DIM + (int(255 * out),))
    if qb > 0:
        y0, y1 = 1080, 1080 - 420 * qb
        d.line((x2, y0, x2, y1), fill=CYAN + (int(255 * out),), width=22)
        d.polygon([(x2 - 50, y1 + 10), (x2 + 50, y1 + 10), (x2, y1 - 60)], fill=CYAN + (int(255 * out),))
    f.alpha_composite(lay)
    place(f, text_img("زبائن تروح", AR, 46, DIM), x1, 1170, qa * out)
    place(f, text_img("زبائن تجي", AR, 46, CYAN), x2, 1170, qb * out)

def scene_send(f, t):
    if t < T_SEND - 0.1 or t > T_OUT + 0.4: return
    out = 1 - prog(t, T_OUT, 0.3)
    p = ease_back(prog(t, T_SEND, 0.45))
    # paper plane flying in a loop
    k = (t - T_SEND)
    x = CX + math.sin(k * 2.2) * 120; y = CY - 40 - k * 40
    s = 150 * (0.6 + 0.4 * p)
    lay, d = overlay(f)
    al = int(255 * clamp(p * 1.5) * out)
    pts = [(x + s, y - s * 0.3), (x - s, y - s * 0.05), (x - s * 0.35, y + s * 0.15), (x - s * 0.2, y + s * 0.7)]
    d.polygon([pts[0], pts[1], pts[2]], fill=WHITE + (al,))
    d.polygon([pts[0], pts[2], pts[3]], fill=CYAN + (al,))
    for j in range(4):  # trail
        tx = x - s - 40 - j * 50; ty = y + 20 + j * 18
        d.ellipse((tx - 8, ty - 8, tx + 8, ty + 8), fill=CYAN + (int(al * (1 - j / 4)),))
    f.alpha_composite(lay)
    place(f, pill("لصاحب محل تعرفه", 50), CX, CY + 300, ease_out(prog(t, T("لصاحب"), 0.3)) * out)

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
    ws = [("محلك", True, T_OUT + 0.9), ("مفتوح", False, T_OUT + 1.2), ("حتى", False, T_OUT + 1.5), ("وإنت", False, T_OUT + 1.8), ("نايم", True, T_OUT + 2.1)]
    imgs = [word_img(w, a) for w, a, _ in ws]; gap = -40
    total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    sc = min(1.0, 960 / total); x = W / 2 + total * sc / 2
    for (w, a, st), im in zip(ws, imgs):
        r = ease_out(prog(t, st, 0.26))
        if r > 0.01: place(f, blurred(w, a, int(round((1 - r) * 8))), x - im.width * sc / 2, 1040 + (1 - r) * 24, r, sc)
        x -= (im.width + gap) * sc
    c = ease_back(prog(t, T_OUT + 2.6, 0.45))
    if c > 0.01:
        btn = rounded(640, 140, 70, BLUE, grad=(BLUE, (0, 160, 255))).copy()
        bt = text_img("راسلنا هسه", AR, 70, WHITE)
        btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
        pulse = 1 + 0.035 * math.sin(t * 6) * prog(t, T_OUT + 3.1, 0.3)
        place(f, btn, CX, 1300, clamp(c * 1.4), (0.8 + 0.2 * c) * pulse)
    dd = ease_out(prog(t, T_OUT + 3.0, 0.4))
    place(f, text_img("WhatsApp  07751027553", EN_SB, 50, WHITE, rtl=False), CX, 1490, dd)
    place(f, text_img("nexodeveloper.net", EN_SB, 46, CYAN, rtl=False), CX, 1570, dd)
    place(f, text_img("Connect to the Future.", EN_SB, 40, GRAY, rtl=False), CX, 1680, ease_out(prog(t, T_OUT + 3.5, 0.5)))

def frame(i):
    t = i / FPS
    f = background(t)
    scene_hook(f, t); scene_before(f, t); scene_after(f, t); scene_web(f, t); scene_diff(f, t); scene_send(f, t)
    wipe(f, t)
    scene_outro(f, t)
    if t < T_OUT: captions(f, t)
    w = int(W * clamp(t / DUR))
    if w > 0: f.alpha_composite(gradient(w, 8, BLUE, CYAN).convert("RGBA"), (0, H - 8))
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "times":
        for k in ["T_BEFORE", "T_AFTER", "T_WEB", "T_DIFF", "T_SEND", "T_OUT"]: print(k, round(globals()[k], 2))
        sys.exit()
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]: frame(int(float(ts) * FPS)).save(f"p_{ts}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "v2.mp4"],
                         stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
