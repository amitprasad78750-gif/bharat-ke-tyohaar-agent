"""Paper cut-out style: Chhathi Maiya ki Katha (12 fps stop-motion look)."""
import math, subprocess, sys, json, random, importlib.util
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, "/home/claude/tts")
import raju_shyam as R
def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
D = _load("dbase", "/home/claude/dhanteras/build.py")

W, H, FPS = 1080, 1920, 12
VJ = json.load(open("/home/claude/paper/vo.json")); SEGS = VJ["segs"]; SEG = {s["id"]: s for s in SEGS}
DUR = SEGS[-1]["end"] + 1.0
OUT = "/home/claude/chhathi_maiya_katha_paper.mp4"
dfont, ease, clamp = R.dfont, R.ease, R.clamp
S = lambda i: SEG[i]["start"]; E = lambda i: SEG[i]["end"]
INK = (70, 30, 20); GOLD = (240, 175, 40)
def at(i, word):
    s = SEG[i]; p = s["text"].find(word) / max(1, len(s["text"])); return s["start"] + (s["end"] - s["start"]) * p - .25

# ---------------- paper helpers ----------------
RNG = np.random.RandomState(7)
GRAIN = Image.fromarray((RNG.normal(1.0, .045, (H, W)).clip(.8, 1.15) * 255 / 1.15).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(.6))
def grain_rgb(im):
    g = GRAIN.crop((0, 0) + im.size) if im.size[0] <= W and im.size[1] <= H else GRAIN.resize(im.size)
    arr = np.asarray(im.convert("RGB")).astype(np.float32) * (np.asarray(g).astype(np.float32)[..., None] / (255 / 1.15))
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))

def cutout(sp, border=9, sh=(12, 16), blur=7):
    """sticker/paper-cut look: white cut border + drop shadow + grain"""
    pad = border + max(sh) + blur * 2
    w, h = sp.size
    a = sp.split()[3]
    big = Image.new("L", (w + 2 * pad, h + 2 * pad), 0); big.paste(a, (pad, pad))
    b = (big.filter(ImageFilter.MaxFilter(border * 2 + 1)) if border > 0 else big).filter(ImageFilter.GaussianBlur(1)).point(lambda v: 255 if v > 90 else 0)
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", big.size, (40, 20, 10, 0)); shadow.putalpha(b.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * .45)))
    out.alpha_composite(shadow, (sh[0], sh[1])) if False else None
    sh_layer = Image.new("RGBA", big.size, (0, 0, 0, 0)); sh_layer.paste(shadow, (sh[0], sh[1]), shadow)
    out = sh_layer
    white = Image.new("RGBA", big.size, (250, 246, 236, 0)); white.putalpha(b)
    out.alpha_composite(white)
    rgb = grain_rgb(sp); spg = rgb.convert("RGBA"); spg.putalpha(a)
    out.alpha_composite(spg, (pad, pad))
    return out, pad

def torn_poly(x0, y0, x1, y1, rr, amp=10, step=26):
    pts = []
    for x in np.arange(x0, x1, step): pts.append((x, y0 + rr.uniform(-amp, amp)))
    for y in np.arange(y0, y1, step): pts.append((x1 + rr.uniform(-amp, amp), y))
    for x in np.arange(x1, x0, -step): pts.append((x, y1 + rr.uniform(-amp, amp)))
    for y in np.arange(y1, y0, -step): pts.append((x0 + rr.uniform(-amp, amp), y))
    return pts

def strip(w, h, col, seed=1):
    sp = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(sp)
    d.polygon(torn_poly(20, 20, w + 20, h + 20, random.Random(seed)), fill=col + (255,))
    return sp

# ---------------- backgrounds ----------------
def bg_base(top, bottom):
    arr = np.zeros((H, W, 3), np.float32)
    for c in range(3): arr[..., c] = np.linspace(top[c], bottom[c], H)[:, None]
    return grain_rgb(Image.fromarray(arr.astype(np.uint8))).convert("RGBA")
def hills(img, y, col, seed, amp=60):
    rr = random.Random(seed); sp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sp)
    pts = [(0, H)] + [(x, y + amp * math.sin(x / 170 + seed) + rr.uniform(-8, 8)) for x in range(0, W + 30, 30)] + [(W, H)]
    d.polygon(pts, fill=col + (255,))
    c, pad = cutout(sp, border=0, sh=(0, -10), blur=10)
    img.alpha_composite(c, (-pad, -pad))
def make_bg(kind):
    if kind == "palace":
        img = bg_base((250, 214, 160), (236, 180, 120))
        hills(img, 1250, (200, 120, 70), 1); hills(img, 1400, (160, 85, 50), 2, 30)
    elif kind == "night":
        img = bg_base((40, 50, 100), (110, 70, 120))
        d = ImageDraw.Draw(img); rr = random.Random(4)
        for _ in range(60):
            x, y, r = rr.uniform(0, W), rr.uniform(150, 1100), rr.uniform(3, 7)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 200, 255))
        hills(img, 1300, (50, 40, 80), 3); hills(img, 1450, (35, 30, 60), 5, 30)
    else:  # ghaat
        img = bg_base((255, 200, 120), (250, 140, 70))
        hills(img, 1080, (120, 70, 60), 6, 40)
        river = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(river)
        d.rectangle([0, 1150, W, H], fill=(70, 120, 170, 255))
        for k in range(9): d.line([(80 + k * 40, 1200 + k * 45), (W - 80 - k * 40, 1200 + k * 45)], fill=(250, 190, 100, 255), width=10)
        c, pad = cutout(river, 0, (0, -8), 8); img.alpha_composite(c, (-pad, -pad))
    return img
BGS = {k: make_bg(k) for k in ("palace", "night", "ghaat")}

# ---------------- paper dolls & props (drawn large, then cut) ----------------
SK = (205, 145, 100)
def face(d, cx, cy, r, mood="smile", eyes="open"):
    if eyes == "closed":
        for k in (-1, 1): d.arc([cx + k * r * .38 - r * .16, cy - r * .2, cx + k * r * .38 + r * .16, cy + r * .08], 200, 340, fill=INK, width=6)
    else:
        for k in (-1, 1): d.ellipse([cx + k * r * .38 - 9, cy - r * .12 - 9, cx + k * r * .38 + 9, cy - r * .12 + 9], fill=INK)
    if mood == "smile": d.arc([cx - r * .35, cy + r * .05, cx + r * .35, cy + r * .5], 20, 160, fill=(150, 40, 40), width=7)
    elif mood == "sad": d.arc([cx - r * .3, cy + r * .35, cx + r * .3, cy + r * .75], 200, 340, fill=(150, 40, 40), width=7)
    else: d.line([(cx - r * .2, cy + r * .45), (cx + r * .2, cy + r * .45)], fill=(150, 40, 40), width=7)
    for k in (-1, 1): d.ellipse([cx + k * r * .55 - 18, cy + r * .2 - 10, cx + k * r * .55 + 18, cy + r * .2 + 10], fill=(240, 130, 120))

def crown(d, cx, y, w):
    d.polygon([(cx - w, y), (cx + w, y), (cx + w * .8, y - w * 1.0), (cx + w * .35, y - w * .5), (cx, y - w * 1.25), (cx - w * .35, y - w * .5), (cx - w * .8, y - w * 1.0)], fill=GOLD, outline=(180, 110, 0))
    d.ellipse([cx - 12, y - w * .55, cx + 12, y - w * .55 + 24], fill=(220, 30, 40))

def doll(kind, mood="smile", eyes="open"):
    sp = Image.new("RGBA", (520, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(sp); cx = 260
    if kind == "raja":
        d.polygon([(cx - 120, 380), (cx + 120, 380), (cx + 170, 860), (cx - 170, 860)], fill=(40, 90, 160))
        d.rectangle([cx - 170, 800, cx + 170, 860], fill=(240, 240, 230))
        d.polygon([(cx - 120, 380), (cx - 40, 380), (cx + 60, 860), (cx - 30, 860)], fill=(240, 180, 40))
        for k in (-1, 1): d.rounded_rectangle([cx + k * 150 - 35, 400, cx + k * 150 + 35, 680], radius=30, fill=(40, 90, 160))
        d.rectangle([cx - 30, 330, cx + 30, 390], fill=SK)
        d.ellipse([cx - 110, 120, cx + 110, 350], fill=SK)
        d.pieslice([cx - 112, 110, cx + 112, 300], 180, 360, fill=(40, 30, 25))
        face(d, cx, 250, 100, mood, eyes)
        d.arc([cx - 60, 260, cx + 60, 330], 200, 340, fill=(40, 30, 25), width=14)  # mustache
        crown(d, cx, 140, 95)
    elif kind == "rani":
        d.polygon([(cx - 110, 380), (cx + 110, 380), (cx + 180, 860), (cx - 180, 860)], fill=(210, 30, 70))
        d.polygon([(cx + 110, 380), (cx + 40, 380), (cx - 150, 860), (cx - 60, 860)], fill=(250, 190, 40))
        for k in (-1, 1): d.rounded_rectangle([cx + k * 140 - 30, 400, cx + k * 140 + 30, 660], radius=28, fill=SK)
        d.rectangle([cx - 28, 330, cx + 28, 390], fill=SK)
        d.ellipse([cx - 160, 110, cx + 160, 380], fill=(40, 30, 25))
        d.ellipse([cx - 105, 125, cx + 105, 350], fill=SK)
        d.pieslice([cx - 108, 115, cx + 108, 270], 180, 360, fill=(40, 30, 25))
        d.ellipse([cx - 10, 180, cx + 10, 200], fill=(220, 20, 30))
        face(d, cx, 250, 95, mood, eyes)
        crown(d, cx, 140, 70)
    elif kind == "rishi":
        d.polygon([(cx - 120, 380), (cx + 120, 380), (cx + 170, 860), (cx - 170, 860)], fill=(240, 130, 30))
        for k in (-1, 1): d.rounded_rectangle([cx + k * 150 - 35, 400, cx + k * 150 + 35, 660], radius=30, fill=(240, 130, 30))
        d.ellipse([cx - 110, 120, cx + 110, 350], fill=SK)
        d.polygon([(cx - 100, 280), (cx + 100, 280), (cx + 50, 520), (cx, 560), (cx - 50, 520)], fill=(250, 250, 250))
        d.ellipse([cx - 60, 40, cx + 60, 150], fill=(245, 245, 245))  # jata bun
        d.pieslice([cx - 112, 110, cx + 112, 280], 180, 360, fill=(245, 245, 245))
        face(d, cx, 230, 95, "smile", "closed")
        for k in range(3): d.line([(cx - 45, 165 + k * 14), (cx + 45, 165 + k * 14)], fill=(255, 255, 255), width=6)
        d.ellipse([cx - 8, 196, cx + 8, 212], fill=(220, 30, 30))
    elif kind == "devi":
        d.ellipse([cx - 220, 20, cx + 220, 460], fill=(255, 220, 90))
        d.ellipse([cx - 190, 50, cx + 190, 430], fill=(255, 240, 160))
        d.polygon([(cx - 120, 380), (cx + 120, 380), (cx + 200, 880), (cx - 200, 880)], fill=(220, 30, 40))
        d.polygon([(cx - 120, 380), (cx - 40, 380), (cx + 150, 880), (cx + 60, 880)], fill=(250, 190, 30))
        for k in range(8): d.ellipse([cx - 200 + k * 50, 840, cx - 180 + k * 50, 860], fill=GOLD)
        d.rounded_rectangle([cx - 190, 400, cx - 120, 640], radius=30, fill=SK)          # left arm down
        d.rounded_rectangle([cx + 120, 300, cx + 190, 520], radius=30, fill=SK)          # right arm raised blessing
        d.ellipse([cx + 115, 240, cx + 195, 330], fill=SK)
        d.rectangle([cx - 28, 330, cx + 28, 390], fill=SK)
        d.ellipse([cx - 150, 110, cx + 150, 400], fill=(30, 25, 20))
        d.ellipse([cx - 100, 125, cx + 100, 345], fill=SK)
        d.ellipse([cx - 10, 175, cx + 10, 195], fill=(220, 20, 30))
        face(d, cx, 250, 92, "smile", eyes)
        crown(d, cx, 140, 85)
        for k in range(5): d.ellipse([cx - 80 + k * 40 - 10, 370, cx - 80 + k * 40 + 10, 390], fill=GOLD)
    return sp

def prop(kind):
    sp = Image.new("RGBA", (520, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(sp); c = 260
    if kind == "havan":
        d.polygon([(c - 200, 300), (c + 200, 300), (c + 150, 470), (c - 150, 470)], fill=(170, 80, 40))
        for k in range(4): d.line([(c - 190 + k * 8, 330 + k * 35), (c + 190 - k * 8, 330 + k * 35)], fill=(200, 110, 60), width=10)
    elif kind == "kheer":
        d.chord([c - 170, 160, c + 170, 420], 0, 180, fill=(190, 190, 200))
        d.ellipse([c - 170, 230, c + 170, 300], fill=(250, 240, 210))
        for k in range(6): d.ellipse([c - 120 + k * 45, 250, c - 100 + k * 45, 270], fill=(230, 180, 70))
    elif kind == "baby":
        d.ellipse([c - 200, 200, c + 200, 360], fill=(250, 245, 225))
        d.ellipse([c + 70, 190, c + 210, 330], fill=SK)
        d.pieslice([c + 70, 185, c + 210, 290], 180, 360, fill=(40, 30, 25))
        for k in range(4): d.arc([c - 180 + k * 60, 210, c - 100 + k * 60, 350], 260, 100, fill=(230, 220, 190), width=6)
    elif kind == "palace":
        d.rectangle([c - 230, 220, c + 230, 500], fill=(250, 235, 200))
        for k in range(-2, 3): d.chord([c + k * 90 - 35, 320, c + k * 90 + 35, 420], 180, 360, fill=(190, 90, 60)); d.rectangle([c + k * 90 - 35, 370, c + k * 90 + 35, 500], fill=(190, 90, 60))
        d.chord([c - 140, 40, c + 140, 330], 180, 360, fill=(240, 180, 60)); d.rectangle([c - 140, 185, c + 140, 230], fill=(240, 180, 60))
        for k in (-1, 1): d.chord([c + k * 200 - 50, 120, c + k * 200 + 50, 260], 180, 360, fill=(240, 180, 60))
        d.polygon([(c, 0), (c + 10, 40), (c - 10, 40)], fill=(220, 40, 40))
    elif kind == "sun":
        for k in range(16):
            an = k * math.pi / 8
            d.polygon([(c + math.cos(an - .12) * 150, c + math.sin(an - .12) * 150), (c + math.cos(an) * 250, c + math.sin(an) * 250), (c + math.cos(an + .12) * 150, c + math.sin(an + .12) * 150)], fill=(255, 170, 30))
        d.ellipse([c - 160, c - 160, c + 160, c + 160], fill=(255, 120, 30)); d.ellipse([c - 120, c - 120, c + 120, c + 120], fill=(255, 200, 60))
    elif kind == "soop":
        d.chord([c - 220, 160, c + 220, 460], 0, 180, fill=(220, 180, 95))
        for k in range(-7, 8): d.line([(c, 310), (c + k * 30, 310 + 140 * math.cos(k / 8 * 1.2))], fill=(170, 130, 60), width=6)
        d.ellipse([c - 160, 180, c - 50, 290], fill=(120, 75, 35)); d.arc([c - 40, 150, c + 120, 300], 200, 320, fill=(250, 210, 40), width=30)
        d.ellipse([c + 90, 220, c + 170, 300], fill=(240, 120, 30)); d.ellipse([c - 30, 250, c + 50, 300], fill=(190, 115, 40))
    return sp

def flame(step):
    sp = Image.new("RGBA", (360, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(sp); rr = random.Random(step)
    for k, col in enumerate(((240, 90, 20), (255, 170, 30), (255, 230, 120))):
        w = 150 * (1 - k * .28); h = 360 * (1 - k * .25) * rr.uniform(.85, 1.05); x = 180 + rr.uniform(-12, 12)
        d.polygon([(x - w, 410), (x - w * .6, 410 - h * .5), (x + rr.uniform(-30, 30), 410 - h), (x + w * .6, 410 - h * .5), (x + w, 410)], fill=col + (255,))
    return sp

CACHE = {}
def sprite(key, fn, scale=1.0, border=9):
    k = (key, scale)
    if k not in CACHE:
        sp = fn()
        if scale != 1.0: sp = sp.resize((int(sp.size[0] * scale), int(sp.size[1] * scale)), Image.LANCZOS)
        CACHE[k] = cutout(sp, border=border)
    return CACHE[k]

def place(img, key, fn, cx, cy, t, scale=1.0, wob=1.2, a=1.0, seed=0, rot=0.0):
    """paste paper sprite centred at cx,cy with stop-motion wobble"""
    sp, pad = sprite(key, fn, scale)
    step = int(t * FPS) // 2
    rr = random.Random(hash((key, step, seed)) & 0xffffffff)
    ang = rot + rr.uniform(-wob, wob); dx, dy = rr.uniform(-2, 2), rr.uniform(-2, 2)
    s2 = sp.rotate(ang, resample=Image.BICUBIC, expand=True) if abs(ang) > .05 else sp
    if a < 1:
        s2 = s2.copy(); s2.putalpha(s2.split()[3].point(lambda v: int(v * a)))
    img.alpha_composite(s2, (int(cx - s2.size[0] / 2 + dx), int(cy - s2.size[1] / 2 + dy)))

def label(img, text, cx, cy, t, col=(255, 250, 235), tc=INK, size=64, seed=3, a=1.0, rot=0.0):
    key = ("lab", text, col, size)
    def mk():
        f = dfont(size); w = int(ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f)) + 70
        sp = strip(w, int(size * 1.6), col, seed); d = ImageDraw.Draw(sp)
        d.text((sp.size[0] / 2, sp.size[1] / 2), text, font=f, fill=tc + (255,), anchor="mm")
        return sp
    place(img, key, mk, cx, cy, t, 1.0, .8, a, seed, rot)

def glowc(img, x, y, r, a, col=(255, 220, 120)):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for k in range(10, 0, -1):
        rr = r * k / 10; d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (int(30 * a),))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(20)))

# ---------------- scenes ----------------
def slide(t, t0, frm, d=.35):  # slide-in offset (paper sliding into frame)
    return frm * (1 - ease((t - t0) / d))

def frame(i):
    t = i / FPS
    if t < S("n2"):            # HOOK: sun + who is the devi?
        img = BGS["ghaat"].copy()
        glowc(img, W / 2, 760, 420, 1)
        place(img, "sun", lambda: prop("sun"), W / 2, 760, t, 1.5, 3, rot=t * 20)
        q = ease((t - .9) / .4)
        place(img, "devi_sil", lambda: devi_silhouette(), W / 2 + 0, 760, t, .62, 1.5, a=q)
        place(img, "soop", lambda: prop("soop"), W / 2, 1360, t, 1.0)
        label(img, "छठ में सूरज के साथ", W / 2, 250, t, size=66, seed=11)
        label(img, "किस देवी की पूजा", W / 2, 390, t, (200, 30, 50), (255, 245, 220), 86, 12)
    elif t < S("n3"):          # king & queen, no child
        img = BGS["palace"].copy()
        place(img, "palace", lambda: prop("palace"), W / 2, 760 + slide(t, S("n2"), -600), t, 1.7)
        place(img, "raja_sad", lambda: doll("raja", "sad"), 330 + slide(t, S("n2") + .2, -500), 1180, t, .82)
        place(img, "rani_sad", lambda: doll("rani", "sad"), 760 + slide(t, S("n2") + .35, 500), 1190, t, .8)
        label(img, "राजा प्रियंवद", 300, 300, t, size=56, seed=21, rot=-3)
        label(img, "रानी मालिनी", 780, 300, t, size=56, seed=22, rot=3)
        q = ease((t - at("n2", "कोई")) / .3)
        label(img, "संतान नहीं", W / 2, 1520, t, (60, 60, 90), (255, 255, 255), 70, 23, a=q)
    elif t < S("n4"):          # yagya + kheer
        img = BGS["palace"].copy()
        place(img, "rishi", lambda: doll("rishi"), 260, 1080 + slide(t, S("n3"), 800), t, .85)
        glowc(img, 640, 1080, 260, 1, (255, 150, 60))
        place(img, ("flame", int(t * FPS) % 4), lambda: flame(int(t * FPS) % 4), 640, 1020, t, .9, 1)
        place(img, "havan", lambda: prop("havan"), 640, 1180, t, 1.0)
        label(img, "महर्षि कश्यप का यज्ञ", W / 2, 290, t, size=70, seed=31)
        q = ease((t - at("n3", "खीर")) / .5)
        if q > 0:
            kx = 640 + (900 - 640) * q; ky = 900 - 260 * math.sin(q * math.pi) + 80 * q
            place(img, "kheer", lambda: prop("kheer"), kx, ky, t, .6)
            place(img, "rani_ok", lambda: doll("rani", "smile"), 900, 1220, t, .62)
            label(img, "यज्ञ की खीर", 860, 640, t, (250, 210, 80), INK, 58, 32, a=q)
    elif t < S("n5"):          # stillborn — gentle, dim
        img = BGS["night"].copy()
        place(img, "raja_cry", lambda: doll("raja", "sad", "closed"), 270, 1060, t, .72, .8)
        place(img, "rani_cry", lambda: doll("rani", "sad", "closed"), 810, 1060, t, .7, .8)
        place(img, "baby_still", lambda: prop("baby"), W / 2, 1370, t, 1.1, .6)
        q = ease((t - at("n4", "टूट")) / .3)
        label(img, "राजा टूट गए", W / 2, 330, t, (60, 60, 90), (255, 255, 255), 76, 41, a=max(q, .0))
        for k in range(3):  # paper tear drops
            ty = 960 + ((t * 120 + k * 60) % 140)
            d = ImageDraw.Draw(img); d.ellipse([225 + k * 3, ty - 60, 245 + k * 3, ty - 30], fill=(120, 170, 240, 220))
    elif t < S("n6"):          # devi appears
        img = BGS["night"].copy()
        q = ease((t - S("n5")) / 1.2)
        glowc(img, W / 2, 760, 520 * q + 50, q)
        place(img, "devi", lambda: doll("devi"), W / 2, 260 + 560 * q, t, 1.0, 1.0)
        place(img, "raja_look", lambda: doll("raja", "neutral"), 230, 1300, t, .62)
        q2 = ease((t - at("n5", "ब्रह्मा")) / .3)
        label(img, "षष्ठी देवी", W / 2, 1440, t, (220, 30, 40), (255, 240, 200), 92, 51, a=q2)
        label(img, "ब्रह्मा जी की मानस पुत्री", W / 2, 1575, t, size=52, seed=52, a=q2)
    elif t < S("n7"):          # blessing → son
        img = BGS["palace"].copy()
        glowc(img, W / 2, 650, 380, 1)
        place(img, "devi", lambda: doll("devi"), W / 2, 820, t, .82, 1.0)
        q = ease((t - at("n6", "व्रत")) / .4)
        place(img, "raja_happy", lambda: doll("raja", "smile"), 230, 1300, t, .62)
        place(img, "rani_happy", lambda: doll("rani", "smile"), 850, 1300, t, .6)
        if q > 0:
            glowc(img, W / 2, 1360, 200, q, (255, 240, 170))
            place(img, "baby_ok", lambda: prop("baby"), W / 2, 1380, t, .9, 3, a=q)
            label(img, "पुत्र प्राप्ति", W / 2, 1560, t, (40, 140, 70), (255, 255, 255), 72, 61, a=q)
        label(img, "मेरी पूजा करो", W / 2, 260, t, size=66, seed=62, a=ease((t - S("n6")) / .3))
    else:                      # CTA: Chhathi Maiya + Surya at ghaat
        img = BGS["ghaat"].copy()
        glowc(img, 760, 520, 360, 1)
        place(img, "sun2", lambda: prop("sun"), 780, 520, t, 1.1, 3, rot=t * 20)
        place(img, "devi2", lambda: doll("devi"), 330, 830, t, .78)
        q = ease((t - at("n7", "सूर्य")) / .3)
        label(img, "छठी मैया", 330, 240, t, (220, 30, 40), (255, 240, 200), 84, 71)
        label(img, "सूर्य देव की बहन", 790, 900, t, size=58, seed=72, a=q, rot=-2)
        q2 = ease((t - at("n7", "बच्चों")) / .3)
        label(img, "बच्चों की रक्षक", 790, 1030, t, size=58, seed=73, a=q2, rot=2)
        q3 = ease((t - at("n7", "कमेंट")) / .3)
        place(img, "soop", lambda: prop("soop"), W / 2, 1330, t, 1.0)
        label(img, "कमेंट करें  जय छठी मैया", W / 2, 1560, t, (200, 30, 50), (255, 245, 220), 70, 74, a=q3)
    # subtitle on paper strip
    for s in SEGS:
        if s["start"] - .05 <= t <= s["end"] + .2:
            words = R.clean(s["text"]).split(); f = dfont(54); lines, cur = [], []
            dd = ImageDraw.Draw(img)
            for w in words:
                if dd.textlength(" ".join(cur + [w]), font=f) > W - 180 and cur: lines.append(cur); cur = [w]
                else: cur.append(w)
            lines.append(cur)
            hh = 70 * len(lines) + 40; y0 = 1800 - hh / 2
            sp = strip(W - 120, int(hh), (255, 250, 235), 99 + len(lines))
            c, pad = cutout(sp, 0, (6, 8), 5) if ("sub", len(lines)) not in CACHE else CACHE[("sub", len(lines))]
            CACHE[("sub", len(lines))] = (c, pad)
            img.alpha_composite(c, (int(60 - 20 - pad), int(y0 - 20 - pad)))
            y = 1800 - (len(lines) - 1) * 35
            for ln in lines: dd.text((W / 2, y), " ".join(ln), font=f, fill=INK + (255,), anchor="mm"); y += 70
    dd = ImageDraw.Draw(img)
    dd.text((W / 2, 70), "भारत के त्योहार", font=dfont(38), fill=(255, 250, 235, 230), anchor="mm", stroke_width=4, stroke_fill=(90, 40, 20, 200))
    if t > S("n2"): dd.text((W / 2, 118), "पौराणिक कथा और मान्यताओं पर आधारित", font=dfont(30), fill=(255, 250, 235, 230), anchor="mm", stroke_width=3, stroke_fill=(90, 40, 20, 200))
    return img.convert("RGB")

def devi_silhouette():
    sp = doll("devi")
    a = sp.split()[3]
    out = Image.new("RGBA", sp.size, (90, 30, 40, 255)); out.putalpha(a)
    d = ImageDraw.Draw(out); d.text((260, 560), "?", font=R.lfont(260) if hasattr(R, "lfont") else dfont(200), fill=(255, 220, 120, 255), anchor="mm")
    return out

def build_audio(path):
    vo, sr = sf.read("/home/claude/paper/vo.wav", dtype="float32"); n = int(DUR * sr); vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]; tt = np.arange(n) / sr
    bed_ = sum(np.sin(2 * np.pi * f * tt + ph) * g for f, g, ph in ((146.8, .5, 0), (220.0, .3, 1), (293.7, .2, 2))) * (1 + .25 * np.sin(2 * np.pi * .2 * tt))
    talk = np.zeros(n, np.float32)
    for s in SEGS: talk[int(s["start"] * sr):int(s["end"] * sr)] = 1
    talk = np.convolve(talk, np.ones(int(.2 * sr)) / int(.2 * sr), mode="same")
    out = vo + (bed_ * .035 * (1 - .7 * np.clip(talk, 0, 1))).astype(np.float32)
    def add(t0, sig):
        st = int(max(0, t0) * sr); m = min(n - st, len(sig))
        if m > 0: out[st:st + m] += sig[:m]
    def bell(f=700, v=.06, L=1.6, dec=3):
        x = np.arange(int(L * sr)) / sr
        return ((np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 2.76 * x)) * np.exp(-x * dec) * v).astype(np.float32)
    def rustle(v=.05):
        x = np.arange(int(.35 * sr)) / sr; nz = np.random.RandomState(3).randn(len(x)).astype(np.float32)
        nz = np.convolve(nz, np.ones(6) / 6, mode="same") - np.convolve(nz, np.ones(60) / 60, mode="same")
        return (nz * np.sin(np.pi * x / x[-1]) * v).astype(np.float32)
    add(0, bell())
    for s in SEGS[1:]: add(s["start"] - .3, rustle()); add(s["start"] - .2, bell(700, .045))
    add(S("n5") + .2, bell(1050, .05, 2.5, 1.5)); add(S("n5") + .6, bell(1400, .04, 2.5, 1.5))
    out[-int(.6 * sr):] *= np.linspace(1, 0, int(.6 * sr))
    out = np.clip(out / max(1.0, np.max(np.abs(out)) / .95), -1, 1)
    raw = path.replace(".wav", "_raw.wav"); sf.write(raw, out, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    "highpass=f=80,equalizer=f=250:width_type=o:width=1:g=-2,equalizer=f=3200:width_type=o:width=1.2:g=4,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000",
                    path], check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        secs = [float(x) for x in sys.argv[1].split(",")]
        ims = [frame(int(s * FPS)).resize((360, 640)) for s in secs]
        g = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): g.paste(im, (k * 360, 0))
        g.save("/home/claude/paper/prev.jpg"); sys.exit()
    wav = "/home/claude/paper/mix.wav"; build_audio(wav)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", OUT], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait(); print("done", DUR)
