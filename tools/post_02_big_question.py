import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from render import text_img, gradient, rounded, place, NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, AR_BLACK, AR_REG, EN, EN_SB

W, H = 1080, 1350
OUT = sys.argv[1] if len(sys.argv) > 1 else "nexo-post.jpg"
f = Image.new("RGBA", (W, H), NAVY + (255,))
def ov():
    l = Image.new("RGBA", f.size, (0, 0, 0, 0)); return l, ImageDraw.Draw(l)

# soft single spotlight + fine grain grid (minimal)
l, d = ov(); d.ellipse((-300, 250, 900, 1350), fill=BLUE + (60,)); f.alpha_composite(l.filter(ImageFilter.GaussianBlur(220)))
l, d = ov()
for x in range(0, W, 54): d.line((x, 0, x, H), fill=(169, 184, 204, 9), width=1)
for y in range(0, H, 54): d.line((0, y, W, y), fill=(169, 184, 204, 9), width=1)
f.alpha_composite(l)

# top: small brand line
place(f, text_img("NEXO", EN, 46, WHITE, rtl=False), 120, 88)
l, d = ov(); d.line((210, 88, W - 300, 88), fill=(169, 184, 204, 50), width=2); f.alpha_composite(l)
place(f, text_img("سؤال صغير…", AR_REG, 34, GRAY), W - 170, 88)

# giant question, right aligned (RTL), three lines
def right(img, y, x_right=W - 70):
    f.alpha_composite(img, (int(x_right - img.width + 40), int(y - img.height / 2)))
right(text_img("زبونك", AR_BLACK, 190, WHITE), 290)
right(text_img("راسلك…", AR_BLACK, 190, WHITE), 490)
right(text_img("وما رديت؟", AR_BLACK, 190, CYAN, glow=14), 690)

# the unanswered message card (left-bottom), tilted slightly
card = rounded(440, 200, 36, DNAVY, border=(169, 184, 204, 110)).copy()
cd = ImageDraw.Draw(card)
cd.ellipse((60 + 310, 58, 60 + 366, 114), fill=(40, 60, 95, 255))          # avatar
av = text_img("ز", AR, 32, WHITE); card.alpha_composite(av, (60 + 338 - av.width // 2, 86 - av.height // 2))
t1 = text_img("زبون جديد", AR, 30, WHITE); card.alpha_composite(t1, (60 + 296 - t1.width + 40, 62))
t2 = text_img("مرحبا، متوفر؟ شكد السعر؟", AR_REG, 27, (200, 208, 220)); card.alpha_composite(t2, (60 + 366 - t2.width + 40, 124))
t3 = text_img("شوهدت · بدون رد", AR_REG, 24, GRAY); card.alpha_composite(t3, (60 + 366 - t3.width + 40, 172))
cd.ellipse((88, 96, 112, 120), fill=(120, 130, 150, 255))
card = card.rotate(4, expand=True, resample=Image.BICUBIC)
place(f, card, 270, 1010)

# answer line + CTA (right column bottom)
l, d = ov(); d.line((W - 70, 880, W - 70, 1140), fill=CYAN + (220,), width=6); f.alpha_composite(l)
right(text_img("خلّي نيكسو يرد بدالك", AR, 44, WHITE), 910, W - 100)
right(text_img("بثانية… حتى بنص الليل", AR, 44, CYAN), 970, W - 100)
right(text_img("موظف مبيعات ذكي", AR_REG, 28, GRAY), 1030, W - 100)
right(text_img("+ موقع احترافي لمحلك", AR_REG, 28, GRAY), 1072, W - 100)
btn = rounded(330, 86, 43, BLUE, grad=(BLUE, (0, 165, 255)), shadow=False).copy()
bt = text_img("راسلنا هسه", AR, 40, WHITE); btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
f.alpha_composite(btn, (int(W - 100 - btn.width + 40), 1130))

# footer
l, d = ov(); d.line((70, 1275, W - 70, 1275), fill=(169, 184, 204, 50), width=2); f.alpha_composite(l)
place(f, text_img("nexodeveloper.net", EN_SB, 30, GRAY, rtl=False), 200, 1310)
place(f, text_img("ماسنجر · إنستا · واتساب", AR_REG, 30, GRAY), W - 220, 1310)

f.convert("RGB").save(OUT, quality=93)
print("ok", OUT)
