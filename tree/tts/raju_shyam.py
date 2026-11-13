import math, subprocess, sys, json, random
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
DJ = json.load(open("/home/claude/tts/dialog.json"))
DUR = DJ["total"]; SEGS = DJ["segs"]; SEG = {s["id"]: s for s in SEGS}
OUT = "/home/claude/raju_shyam_kasam.mp4"
FD = "/home/claude/tts/font/package/files/noto-sans-devanagari-devanagari-%d-normal.woff"
FL = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_f = {}
def dfont(size, wt=800):
    k = (int(size), wt)
    if k not in _f: _f[k] = ImageFont.truetype(FD % wt, int(size))
    return _f[k]
def lfont(size):
    k = (int(size), "L")
    if k not in _f: _f[k] = ImageFont.truetype(FL, int(size))
    return _f[k]
def lerp(a, b, t): return a + (b - a) * t
def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def win(t, a, b, f=0.3): return ease((t - a) / f) * ease((b - t) / f)
def S(i): return SEG[i]["start"]
def E(i): return SEG[i]["end"]

# ---------- lip sync envelope ----------
_dw, _sr = sf.read("/home/claude/tts/dialog.wav", dtype="float32")
_hop = _sr // FPS
ENV = np.array([np.sqrt(np.mean(_dw[i * _hop:(i + 1) * _hop] ** 2) + 1e-9) for i in range(len(_dw) // _hop + 1)])
ENV = np.clip(ENV / 0.12, 0, 1)
def speaking(who, t):
    for s in SEGS:
        if s["start"] <= t <= s["end"] and (s["spk"] == who or (s["spk"] == "both" and who in ("raju", "shyam")) or (s["spk"] == "narr" and who == "raju")):
            return float(ENV[min(len(ENV) - 1, int(t * FPS))])
    return None

# ---------- characters ----------
RAJU = dict(kurta=(240, 190, 50), bottom=(245, 242, 230), btype="dhoti", skin=(196, 140, 98), hair="messy", mus=2, build=1.2, female=False, gam=(200, 50, 50))
SHYAM = dict(kurta=(70, 120, 190), bottom=(60, 130, 90), btype="lungi", skin=(186, 132, 92), hair="side", mus=0, build=0.95, female=False, gam=None)
WIFE1 = dict(kurta=(210, 40, 60), bottom=(210, 40, 60), btype="saree", skin=(205, 150, 108), hair="bun", mus=0, build=1.0, female=True, gam=None)
WIFE2 = dict(kurta=(40, 150, 90), bottom=(40, 150, 90), btype="saree", skin=(200, 145, 104), hair="bun", mus=0, build=1.0, female=True, gam=None)
UNCLE = dict(kurta=(245, 245, 240), bottom=(90, 90, 150), btype="lungi", skin=(180, 125, 85), hair="bald", mus=2, build=1.45, female=False, gam=(240, 170, 30), vest=True)

def broom_item(d, hx, hy, s, ang):
    ex = hx + math.sin(ang) * 110 * s; ey = hy - math.cos(ang) * 110 * s
    d.line([(hx, hy), (ex, ey)], fill=(150, 100, 50), width=int(7 * s))
    for k in range(-4, 5):
        a2 = ang + k * 0.06
        d.line([(ex, ey), (ex + math.sin(a2) * 50 * s, ey - math.cos(a2) * 50 * s)], fill=(200, 170, 90), width=max(2, int(3 * s)))

def cup(d, x, y, s):
    d.polygon([(x - 9 * s, y - 14 * s), (x + 9 * s, y - 14 * s), (x + 7 * s, y + 8 * s), (x - 7 * s, y + 8 * s)], fill=(240, 240, 235), outline=(150, 150, 150))
    d.rectangle([x - 8 * s, y - 12 * s, x + 8 * s, y - 6 * s], fill=(170, 110, 60))

def char(d, P, x, y, s, pose="stand", mouth="smile", mo=None, eyes="open", arms="down", ph=0.0, look=0, lean=0, item=None):
    """mo: lip openness 0..1 when speaking (overrides mouth)."""
    skin = P["skin"]; dark = mix(skin, (0, 0, 0), 0.3); kur = P["kurta"]; bot = P["bottom"]
    bw = 27 * P["build"] * s
    if pose == "sit":
        hip = y - 28 * s
    else:
        hip = y - 70 * s
    sh = hip - 62 * s; hr = 27 * s; hy = sh - hr - 6 * s
    lx = lean * s  # upper body shift
    # ---- legs ----
    if pose == "sit":
        d.rounded_rectangle([x - 50 * s, y - 34 * s, x + 50 * s, y], radius=int(16 * s), fill=bot if P["btype"] != "saree" else bot)
        for k in (-1, 1): d.ellipse([x + k * 46 * s - 12 * s, y - 14 * s, x + k * 46 * s + 12 * s, y + 4 * s], fill=skin)
    else:
        sw = math.sin(ph) * (34 if pose == "run" else 14) * s if pose in ("run", "walk") else 0
        lift = abs(math.cos(ph)) * 14 * s if pose == "run" else 0
        if P["btype"] == "saree":
            d.polygon([(x - bw, hip - 8 * s), (x + bw, hip - 8 * s), (x + bw * 1.2, y), (x - bw * 1.2, y)], fill=bot)
            d.line([(x - bw * 1.15, y - 14 * s), (x + bw * 1.15, y - 14 * s)], fill=mix(bot, (255, 220, 100), 0.6), width=max(2, int(5 * s)))
            for k, p in ((-1, 1), (1, -1)):
                fx = x + k * 11 * s + p * sw * 0.4
                d.ellipse([fx - 11 * s, y - 6 * s, fx + 11 * s, y + 4 * s], fill=(90, 55, 30))
        else:
            dh = 16 * s if P["btype"] == "dhoti" else 30 * s
            d.polygon([(x - bw * 0.9, hip - 6 * s), (x + bw * 0.9, hip - 6 * s), (x + bw * 0.85, y - dh), (x - bw * 0.85, y - dh)], fill=bot)
            if P["btype"] == "lungi":
                for i in range(3):
                    yy = hip + i * 12 * s
                    d.line([(x - bw * 0.88, yy), (x + bw * 0.88, yy)], fill=mix(bot, (255, 255, 255), 0.35), width=max(1, int(2 * s)))
            for k, p in ((-1, 1), (1, -1)):
                fx = x + k * 11 * s + p * sw
                fy = y - (lift if p * math.sin(ph) > 0 else 0)
                d.line([(x + k * 10 * s, y - dh - 2 * s), (fx, fy - 4 * s)], fill=skin, width=int(10 * s))
                d.ellipse([fx - 12 * s, fy - 7 * s, fx + 12 * s, fy + 4 * s], fill=(90, 55, 30))
    # ---- torso ----
    X = x + lx
    if P.get("vest"):
        d.ellipse([X - bw * 1.1, sh - 4 * s, X + bw * 1.1, hip + 26 * s], fill=kur)
        d.arc([X - 16 * s, sh - 14 * s, X + 16 * s, sh + 18 * s], 20, 160, fill=mix(kur, (0, 0, 0), 0.2), width=max(2, int(3 * s)))
    else:
        d.rounded_rectangle([X - bw, sh - 3 * s, X + bw * 1.0 if True else 0, hip + (22 if not P["female"] else 2) * s], radius=int(12 * s), fill=kur)
    if P["female"]:
        d.polygon([(X - bw, sh), (X - 6 * s, sh), (X + bw, hip - 6 * s), (X + bw, hip + 2 * s)], fill=mix(bot, (255, 255, 255), 0.25))
    elif P.get("gam"):
        d.polygon([(X - bw, sh + 2 * s), (X - bw * 0.45, sh - 4 * s), (X + bw * 0.75, hip - 20 * s), (X + bw * 0.5, hip - 6 * s)], fill=P["gam"])
    if not P.get("vest") and not P["female"]:
        for i in range(3): d.ellipse([X - 2.5 * s, sh + (12 + 14 * i) * s, X + 2.5 * s, sh + (17 + 14 * i) * s], fill=mix(kur, (0, 0, 0), 0.35))
    # ---- arms ----
    aw = int(11 * s)
    Ls, Rs = (X - bw + 2 * s, sh + 9 * s), (X + bw - 2 * s, sh + 9 * s)
    acol = kur if not P.get("vest") else skin
    def arm(a, h, hand=True):
        d.line([a, h], fill=acol, width=aw)
        if hand: d.ellipse([h[0] - 7 * s, h[1] - 7 * s, h[0] + 7 * s, h[1] + 7 * s], fill=skin)
    if arms == "broom_up":
        ang = math.sin(ph) * 0.9
        hx, hy2 = X + 10 * s, sh - 50 * s
        arm(Ls, (hx - 8 * s, hy2 + 6 * s)); arm(Rs, (hx + 6 * s, hy2))
        broom_item(d, hx, hy2, s, ang)
    elif arms == "run":
        sw = math.sin(ph) * 30 * s
        arm(Ls, (X - bw - 14 * s + sw, hip - 10 * s)); arm(Rs, (X + bw + 14 * s - sw, hip - 10 * s))
    elif arms == "cross":
        arm(Ls, (X + 14 * s, sh + 34 * s)); arm(Rs, (X - 14 * s, sh + 30 * s))
    elif arms == "salute":
        arm(Ls, (X - bw - 6 * s, hip)); arm(Rs, (X + 6 * s, hy - 10 * s))
    elif arms == "cup":
        arm(Ls, (X - bw - 6 * s, hip)); arm(Rs, (X + 18 * s, sh + 34 * s)); cup(d, X + 18 * s, sh + 22 * s, s)
    elif arms == "cup_sip":
        arm(Ls, (X - bw - 6 * s, hip)); arm(Rs, (X + 12 * s, hy + 18 * s), hand=False); cup(d, X + 12 * s, hy + 12 * s, s)
    elif arms == "fist_up":
        arm(Ls, (X - bw - 20 * s, sh - 60 * s)); arm(Rs, (X + bw + 20 * s, sh - 60 * s))
    elif arms == "shake_r":   # right arm forward to the right
        arm(Ls, (X - bw - 6 * s, hip)); arm(Rs, (X + bw + 46 * s, sh + 36 * s))
    elif arms == "shake_l":
        arm(Rs, (X + bw + 6 * s, hip)); arm(Ls, (X - bw - 46 * s, sh + 36 * s))
    elif arms == "hug_r":
        arm(Ls, (X + bw + 40 * s, sh + 20 * s)); arm(Rs, (X + bw + 56 * s, sh + 8 * s))
    elif arms == "hug_l":
        arm(Ls, (X - bw - 56 * s, sh + 8 * s)); arm(Rs, (X - bw - 40 * s, sh + 20 * s))
    elif arms == "dance":
        a1 = math.sin(ph) * 40 * s
        arm(Ls, (X - bw - 30 * s, sh - 30 * s + a1)); arm(Rs, (X + bw + 30 * s, sh - 30 * s - a1))
    elif arms == "think":
        arm(Ls, (X - bw - 6 * s, hip)); arm(Rs, (X + 8 * s, hy + 26 * s))
    elif arms == "point":
        arm(Ls, (X - bw - 6 * s, hip)); arm(Rs, (X + bw + 50 * s, sh + 4 * s))
    elif arms == "point_l":
        arm(Rs, (X + bw + 6 * s, hip)); arm(Ls, (X - bw - 50 * s, sh + 4 * s))
    elif arms == "wash":
        sw = math.sin(ph * 2) * 10 * s
        arm(Ls, (X - 18 * s + sw, hip + 4 * s)); arm(Rs, (X + 18 * s - sw, hip + 4 * s))
    elif arms == "hips":
        arm(Ls, (X - bw - 18 * s, sh + 34 * s)); arm(Rs, (X + bw + 18 * s, sh + 34 * s))
        d.line([(X - bw - 18 * s, sh + 34 * s), (X - bw + 2 * s, hip - 4 * s)], fill=acol, width=aw)
        d.line([(X + bw + 18 * s, sh + 34 * s), (X + bw - 2 * s, hip - 4 * s)], fill=acol, width=aw)
    elif arms == "knee":
        arm(Ls, (X - 40 * s, y - 30 * s)); arm(Rs, (X + 40 * s, y - 30 * s))
    else:
        arm(Ls, (X - bw - 6 * s, hip + 2 * s)); arm(Rs, (X + bw + 6 * s, hip + 2 * s))
    # ---- head ----
    d.rectangle([X - 8 * s, sh - 10 * s, X + 8 * s, sh], fill=skin)
    if P["hair"] == "bun": d.ellipse([X - 13 * s, hy - hr - 12 * s, X + 13 * s, hy - hr + 10 * s], fill=P.get("hc", (30, 25, 20)))
    d.ellipse([X - hr, hy - hr, X + hr, hy + hr], fill=skin, outline=dark)
    for k in (-1, 1): d.ellipse([X + k * hr - 5 * s, hy - 3 * s, X + k * hr + 5 * s, hy + 8 * s], fill=skin)
    hc = P.get("hc", (30, 25, 20))
    if P["hair"] == "messy":
        d.chord([X - hr, hy - hr - 4 * s, X + hr, hy + hr * 0.3], 180, 360, fill=hc)
        for i in range(-3, 4):
            d.polygon([(X + i * 8 * s - 5 * s, hy - hr + 2 * s), (X + i * 8 * s + 5 * s, hy - hr + 2 * s), (X + i * 9 * s, hy - hr - 12 * s)], fill=hc)
    elif P["hair"] == "side":
        d.chord([X - hr, hy - hr - 3 * s, X + hr, hy + hr * 0.4], 180, 360, fill=hc)
        d.polygon([(X - hr, hy - 8 * s), (X - 4 * s, hy - hr - 4 * s), (X + hr * 0.4, hy - hr + 4 * s)], fill=hc)
    elif P["hair"] == "bald":
        for k in (-1, 1): d.ellipse([X + k * hr - 7 * s, hy - 10 * s, X + k * hr + 7 * s, hy + 4 * s], fill=(60, 55, 50))
        d.arc([X - 10 * s, hy - hr + 3 * s, X + 4 * s, hy - hr + 12 * s], 200, 300, fill=(255, 255, 255), width=max(2, int(3 * s)))
    elif P["hair"] == "bun":
        d.chord([X - hr - 3 * s, hy - hr - 3 * s, X + hr + 3 * s, hy + hr * 0.5], 180, 360, fill=hc)
        d.line([(X, hy - hr - 2 * s), (X, hy - hr + 8 * s)], fill=(220, 30, 30), width=max(2, int(3 * s)))
        d.ellipse([X - 3 * s, hy - 13 * s, X + 3 * s, hy - 7 * s], fill=(210, 20, 30))
    # eyes
    lk = look * 5 * s; ey = hy - 1 * s
    for k in (-1, 1):
        ex = X + k * 10 * s + lk
        if eyes == "closed":
            d.arc([ex - 6 * s, ey - 4 * s, ex + 6 * s, ey + 4 * s], 20, 160, fill=(20, 20, 20), width=max(2, int(3 * s)))
        elif eyes == "happy":
            d.arc([ex - 6 * s, ey - 2 * s, ex + 6 * s, ey + 6 * s], 200, 340, fill=(20, 20, 20), width=max(2, int(3 * s)))
        elif eyes == "big":
            d.ellipse([ex - 8 * s, ey - 8 * s, ex + 8 * s, ey + 8 * s], fill=(255, 255, 255), outline=(20, 20, 20), width=max(1, int(2 * s)))
            d.ellipse([ex - 3.5 * s + lk * 0.3, ey - 3.5 * s, ex + 3.5 * s + lk * 0.3, ey + 3.5 * s], fill=(20, 20, 20))
        elif eyes == "half":
            d.ellipse([ex - 4 * s, ey - 2 * s, ex + 4 * s, ey + 4 * s], fill=(20, 20, 20))
            d.line([(ex - 7 * s, ey - 1 * s), (ex + 7 * s, ey - 1 * s)], fill=dark, width=max(2, int(4 * s)))
        elif eyes == "sly":
            d.ellipse([ex - 3.5 * s, ey - 2 * s, ex + 3.5 * s, ey + 4 * s], fill=(20, 20, 20))
            d.line([(ex - 7 * s, ey - 4 * s), (ex + 7 * s, ey - 1 * s)], fill=dark, width=max(2, int(4 * s)))
        else:
            d.ellipse([ex - 4 * s, ey - 4 * s, ex + 4 * s, ey + 4 * s], fill=(20, 20, 20))
        if mouth == "angry" or eyes == "angry":
            d.line([(X + k * 16 * s + lk, ey - 12 * s), (X + k * 4 * s + lk, ey - 6 * s)], fill=(30, 20, 20), width=max(2, int(4 * s)))
        if mouth in ("sad", "cry"):
            d.line([(X + k * 16 * s + lk, ey - 7 * s), (X + k * 4 * s + lk, ey - 11 * s)], fill=(30, 20, 20), width=max(2, int(3 * s)))
    if mouth == "cry":
        for k in (-1, 1):
            ty = ey + 8 * s + ((ph * 20) % 30) * s
            d.ellipse([X + k * 11 * s - 4 * s, ty - 4 * s, X + k * 11 * s + 4 * s, ty + 6 * s], fill=(100, 170, 255))
    if P["female"]: pass
    my = hy + 14 * s
    if P["mus"]:
        mw = 15 * s if P["mus"] == 2 else 11 * s
        d.chord([X - mw, my - 9 * s, X + mw, my + 2 * s], 180, 360, fill=(35, 28, 22)); my += 3 * s
    mc = (120, 40, 40)
    if mo is not None:
        o = 2 * s + mo * 14 * s
        d.ellipse([X - 9 * s, my - o / 2 + 2 * s, X + 9 * s, my + o / 2 + 2 * s], fill=mc)
    elif mouth == "angry":
        d.chord([X - 10 * s, my - 2 * s, X + 10 * s, my + 12 * s], 180, 360, fill=mc)
    elif mouth == "laugh":
        d.chord([X - 12 * s, my - 6 * s, X + 12 * s, my + 12 * s], 0, 180, fill=mc)
    elif mouth in ("sad", "cry"):
        d.arc([X - 9 * s, my + 1 * s, X + 9 * s, my + 12 * s], 200, 340, fill=mc, width=max(2, int(3 * s)))
    elif mouth == "O":
        d.ellipse([X - 6 * s, my - 2 * s, X + 6 * s, my + 12 * s], fill=mc)
    elif mouth == "grin":
        d.arc([X - 12 * s, my - 8 * s, X + 8 * s, my + 6 * s], 10, 150, fill=mc, width=max(2, int(4 * s)))
    elif mouth == "flat":
        d.line([(X - 7 * s, my + 2 * s), (X + 7 * s, my + 2 * s)], fill=mc, width=max(2, int(3 * s)))
    else:
        d.arc([X - 10 * s, my - 6 * s, X + 10 * s, my + 5 * s], 20, 160, fill=mc, width=max(2, int(3 * s)))
    return (X, hy - hr, hy)

def sweat(d, x, y, s, t):
    for i in range(2):
        p = (t * 1.5 + i * 0.5) % 1
        yy = y + p * 40 * s; xx = x + (i * 2 - 1) * 34 * s
        d.polygon([(xx, yy - 8 * s), (xx - 5 * s, yy + 2 * s), (xx + 5 * s, yy + 2 * s)], fill=(140, 200, 255))
        d.ellipse([xx - 5 * s, yy - 2 * s, xx + 5 * s, yy + 6 * s], fill=(140, 200, 255))

def bottle(d, x, y, s, ang=0, col=(110, 70, 30)):
    im = Image.new("RGBA", (int(60 * s), int(150 * s)), (0, 0, 0, 0)); bd = ImageDraw.Draw(im)
    w, h = im.size
    bd.rounded_rectangle([w * 0.2, h * 0.38, w * 0.8, h * 0.98], radius=int(8 * s), fill=col + (255,))
    bd.polygon([(w * 0.2, h * 0.4), (w * 0.38, h * 0.2), (w * 0.62, h * 0.2), (w * 0.8, h * 0.4)], fill=col + (255,))
    bd.rectangle([w * 0.38, h * 0.02, w * 0.62, h * 0.22], fill=col + (255,))
    bd.rectangle([w * 0.36, 0, w * 0.64, h * 0.07], fill=(200, 40, 40, 255))
    bd.rectangle([w * 0.25, h * 0.55, w * 0.75, h * 0.78], fill=(245, 230, 190, 255))
    bd.rectangle([w * 0.3, h * 0.42, w * 0.38, h * 0.9], fill=(255, 255, 255, 90))
    im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
    return im, (int(x - im.size[0] / 2), int(y - im.size[1] / 2))

def paste_bottle(img, x, y, s, ang=0):
    im, pos = bottle(None, x, y, s, ang); img.paste(im, pos, im)

# ---------- text helpers ----------
NAME = {"raju": ("राजू", (255, 205, 60)), "shyam": ("श्याम", (120, 190, 255)), "wife1": ("राजू की बीवी", (255, 110, 120)),
        "wife2": ("श्याम की बीवी", (120, 230, 150)), "uncle": ("ठेका अंकल", (255, 170, 80)), "both": ("राजू और श्याम", (255, 255, 255)), "narr": ("राजू", (255, 205, 60))}
def clean(t):
    out = []
    for ch in t:
        if 'ऀ' <= ch <= 'ॿ' or ch == ' ': out.append(ch)
    return ' '.join(''.join(out).split())

def subtitle(o, t):
    for s in SEGS:
        if s["start"] - 0.1 <= t <= s["end"] + 0.3:
            a = win(t, s["start"] - 0.1, s["end"] + 0.3, 0.12)
            od = ImageDraw.Draw(o); f = dfont(54, 700)
            words = clean(s["text"]).split(); lines, cur = [], ""
            for w in words:
                tst = (cur + " " + w).strip()
                if od.textlength(tst, font=f) > W - 150: lines.append(cur); cur = w
                else: cur = tst
            lines.append(cur)
            lh = 76; tot = lh * len(lines) + 56; y0 = 1880 - tot - 30
            od.rounded_rectangle([40, y0, W - 40, y0 + tot + 24], radius=30, fill=(0, 0, 0, int(185 * a)))
            nm, col = NAME[s["spk"]]
            od.text((80, y0 + 34), nm, font=dfont(40), anchor="lm", fill=col + (int(255 * a),))
            for i, l in enumerate(lines):
                od.text((W / 2, y0 + 64 + lh * i + lh / 2), l, font=f, anchor="mm", fill=(255, 255, 255, int(255 * a)))

def dtext(o, xy, text, size, color, a=1.0, stroke=(60, 20, 0), sw=8, wt=800, anchor="mm", font=None):
    if a <= 0.01: return
    od = ImageDraw.Draw(o); A = int(255 * a)
    od.text(xy, text, font=font or dfont(size, wt), anchor=anchor, fill=tuple(color) + (A,), stroke_width=sw, stroke_fill=tuple(stroke) + (A,))

def warning(o, a=1.0):
    od = ImageDraw.Draw(o); A = int(255 * a)
    od.rounded_rectangle([200, 20, W - 200, 78], radius=14, fill=(0, 0, 0, int(150 * a)))
    od.text((W / 2, 49), "शराब का सेवन स्वास्थ्य के लिए हानिकारक है", font=dfont(30, 700), anchor="mm", fill=(255, 255, 255, A))

def bubble(o, x, y, w, h, a, tail):
    od = ImageDraw.Draw(o); A = int(255 * a)
    od.ellipse([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=(255, 255, 255, A), outline=(40, 40, 40, A), width=5)
    for i, (tx, ty, r) in enumerate(tail):
        od.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(255, 255, 255, A), outline=(40, 40, 40, A), width=4)

def compose(img, o): return Image.alpha_composite(img.convert("RGBA"), o).convert("RGB")
def zoom(img, cx, cy, z):
    if z <= 1.001: return img
    w, h = W / z, H / z
    x0 = max(0, min(W - w, cx - w / 2)); y0 = max(0, min(H - h, cy - h / 2))
    return img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BICUBIC)

def vgrad(top, bot, y0=0, y1=H):
    img = Image.new("RGB", (W, H), bot); d = ImageDraw.Draw(img)
    for y in range(y0, y1): d.line([(0, y), (W, y)], fill=mix(top, bot, (y - y0) / max(1, y1 - y0)))
    return img

# ---------- backgrounds ----------
def bg_house_in():
    img = Image.new("RGB", (W, H), (226, 196, 150)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 1300], fill=(214, 180, 130))
    for i in range(0, W, 140): d.line([(i, 0), (i + 30, 1300)], fill=(200, 165, 118), width=3)
    d.line([(300, 350), (340, 420), (320, 480), (360, 560)], fill=(150, 110, 70), width=4)  # crack
    d.rectangle([0, 1300, W, H], fill=(170, 120, 80))
    d.rectangle([860, 650, 1060, 1300], fill=(110, 70, 40), outline=(70, 40, 20), width=8)  # door
    d.rectangle([60, 600, 300, 780], fill=(150, 200, 230), outline=(110, 70, 40), width=10)
    # charpai
    d.rectangle([100, 1180, 560, 1230], fill=(150, 100, 50))
    for x in (110, 540): d.rectangle([x, 1230, x + 20, 1320], fill=(120, 80, 40))
    for i in range(12): d.line([(110 + i * 38, 1182), (130 + i * 38, 1228)], fill=(220, 200, 150), width=3)
    return img
def bg_house_out():
    img = vgrad((150, 205, 245), (220, 236, 250), 0, 1100); d = ImageDraw.Draw(img)
    d.rectangle([140, 450, 940, 1350], fill=(200, 140, 80), outline=(120, 80, 40), width=6)
    d.polygon([(100, 450), (540, 230), (980, 450)], fill=(150, 100, 45))
    d.rectangle([0, 1350, W, H], fill=(196, 160, 110))
    return img
def bg_courtyard():
    img = vgrad((150, 205, 245), (220, 236, 250), 0, 900); d = ImageDraw.Draw(img)
    d.rectangle([0, 520, W, 1250], fill=(225, 190, 140)); d.rectangle([0, 1250, W, H], fill=(180, 150, 110))
    d.rectangle([700, 900, 760, 1250], fill=(70, 90, 100))  # handpump
    d.rectangle([660, 880, 860, 910], fill=(70, 90, 100)); d.line([(760, 900), (880, 840)], fill=(70, 90, 100), width=12)
    for i, (x, y, r) in enumerate([(160, 1330, 50), (240, 1350, 40), (110, 1370, 36), (300, 1320, 30)]):
        d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=(190, 190, 200), outline=(130, 130, 140), width=3)
    return img
def bg_chowk():
    img = vgrad((140, 200, 245), (250, 235, 205), 0, 1100); d = ImageDraw.Draw(img)
    d.rectangle([0, 1100, W, H], fill=(200, 170, 120))
    d.rectangle([640, 650, 1040, 1100], fill=(120, 80, 50))  # chai stall
    d.polygon([(610, 650), (1070, 650), (1020, 560), (660, 560)], fill=(220, 60, 50))
    d.rectangle([680, 700, 1000, 760], fill=(250, 230, 160)); d.text((840, 730), "चाय", font=dfont(48), anchor="mm", fill=(150, 40, 20))
    d.ellipse([700, 820, 790, 900], fill=(170, 170, 180)); d.rectangle([740, 780, 760, 830], fill=(120, 120, 130))
    d.rectangle([150, 760, 200, 1100], fill=(110, 70, 40))
    for cx, cy, r in [(175, 700, 140), (90, 760, 90), (260, 760, 90)]: d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 60))
    return img
ROADW = 3600
def bg_road():
    img = Image.new("RGB", (ROADW, H)); d = ImageDraw.Draw(img)
    for y in range(1100): d.line([(0, y), (ROADW, y)], fill=mix((140, 200, 245), (240, 230, 210), y / 1100))
    d.rectangle([0, 1100, ROADW, 1250], fill=(150, 190, 90))
    d.rectangle([0, 1250, ROADW, 1600], fill=(110, 110, 115))
    for x in range(0, ROADW, 160): d.rectangle([x, 1415, x + 80, 1430], fill=(240, 240, 240))
    d.rectangle([0, 1600, ROADW, H], fill=(150, 190, 90))
    random.seed(4)
    for x in range(80, ROADW, 330):
        if 2100 < x < 2900: continue
        d.rectangle([x, 880, x + 26, 1110], fill=(110, 70, 40)); d.ellipse([x - 80, 760, x + 106, 940], fill=(70, 150, 70))
    # theka at 2200-2850
    tx = 2200
    d.rectangle([tx, 700, tx + 650, 1250], fill=(70, 120, 90), outline=(30, 60, 40), width=8)
    d.rectangle([tx - 20, 610, tx + 670, 720], fill=(230, 40, 40), outline=(120, 10, 10), width=6)
    d.text((tx + 325, 665), "देसी ठेका", font=dfont(80), anchor="mm", fill=(255, 240, 120), stroke_width=4, stroke_fill=(90, 0, 0))
    d.rectangle([tx + 60, 780, tx + 420, 1080], fill=(40, 30, 25))
    for r in range(3):
        for c in range(6):
            bx, by = tx + 90 + c * 55, 830 + r * 85
            d.rounded_rectangle([bx, by, bx + 26, by + 60], radius=5, fill=[(110, 70, 30), (60, 120, 60), (140, 90, 40)][(r + c) % 3])
    for gx in range(tx + 60, tx + 421, 30): d.line([(gx, 780), (gx, 1080)], fill=(140, 140, 150), width=3)
    d.rectangle([tx + 470, 820, tx + 600, 1250], fill=(100, 60, 30), outline=(50, 30, 15), width=5)  # door
    d.rectangle([tx + 100, 1210, tx + 200, 1250], fill=(120, 80, 40))  # stool
    return img
def bg_corner():
    img = Image.new("RGB", (W, H), (190, 160, 120)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 1150], fill=(205, 175, 135)); d.line([(540, 0), (540, 1150)], fill=(170, 140, 100), width=6)
    for x, y in [(80, 980), (200, 1020), (850, 990)]: d.rectangle([x, y, x + 130, y + 130], fill=(160, 110, 60), outline=(110, 70, 30), width=5)
    d.rectangle([0, 1150, W, H], fill=(180, 150, 105))
    return img
def bg_field_evening():
    img = vgrad((40, 30, 90), (240, 120, 80), 0, 1200); d = ImageDraw.Draw(img)
    d.rectangle([0, 1200, W, H], fill=(90, 110, 60))
    random.seed(2)
    for _ in range(60):
        x, y = random.randint(0, W), random.randint(0, 700); d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 230))
    return img
BG = dict(hin=bg_house_in(), hout=bg_house_out(), court=bg_courtyard(), chowk=bg_chowk(), corner=bg_corner(), field=bg_field_evening())
ROAD = bg_road()
def road_view(cam):
    cam = max(0, min(ROADW - W, cam)); return ROAD.crop((int(cam), 0, int(cam) + W, H)), cam

# ---------- scenes ----------
def sc1(t):  # 0 - 9.3 : chase, door, panting
    if t < 6.6:
        img = BG["hin"].copy(); d = ImageDraw.Draw(img)
        # chase loop: Raju runs left->right, wife behind
        cyc = (t * 0.55) % 1.0
        rx = lerp(-150, 1250, cyc); wx = rx - 300
        if t > 5.4:  # final dash to door
            p = (t - 5.4) / 1.2; rx = lerp(500, 960, p); wx = rx - 330
        mo = speaking("wife1", t)
        char(d, WIFE1, wx, 1560, 2.0, pose="run", mo=mo, mouth="angry", eyes="angry", arms="broom_up", ph=t * 12, lean=8)
        char(d, RAJU, rx, 1580, 2.1, pose="run", mouth="O", eyes="big", arms="run", ph=t * 14, lean=10, look=-1)
        # empty bottles on floor
        for bx in (620, 700):
            pass
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        paste_bottle(img, 640, 1330, 0.8, 80); paste_bottle(img, 760, 1340, 0.8, -70)
        dtext(o, (W / 2, 230), "राजू का घर", 90, (255, 255, 255), 1.0 if t > 0 else 0, stroke=(120, 40, 0))
    else:
        img = BG["hout"].copy(); d = ImageDraw.Draw(img)
        d.rectangle([440, 850, 640, 1350], fill=(110, 70, 40), outline=(70, 40, 20), width=8)
        shake = math.sin(t * 60) * 6 * clamp(1 - (t - 6.9) / 0.6) if t > 6.9 else 0
        if t < 6.95:
            d.rectangle([440, 850, 470, 1350], fill=(40, 25, 15))
        img2 = img
        char(d, RAJU, 760, 1580 + shake, 2.3, mouth="O", mo=speaking("raju", t), eyes="closed" if t > 7.3 else "big", arms="down", look=-1)
        sweat(d, 760, 900, 2.3, t)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if 6.85 < t < 7.6:
            dtext(o, (540, 760), "धड़ाम", 110, (255, 230, 80), win(t, 6.85, 7.6, 0.1), stroke=(150, 30, 0))
    subtitle(o, t)
    return compose(img, o)

def sc2(t):  # 9.3 - 16.4
    img = BG["court"].copy(); d = ImageDraw.Draw(img)
    # basin
    d.ellipse([110, 1440, 470, 1560], fill=(160, 160, 175), outline=(110, 110, 120), width=4)
    mo = speaking("wife2", t)
    char(d, WIFE2, 290, 1520, 2.0, mo=mo, mouth="angry", eyes="angry", arms="wash" if mo is None else "point", ph=t * 4, look=1)
    d.ellipse([110, 1480, 470, 1600], fill=(170, 170, 185), outline=(110, 110, 120), width=4)
    for i in range(4):
        bx = 170 + i * 80; d.ellipse([bx, 1490, bx + 60, 1520], fill=(220, 220, 230), outline=(150, 150, 160))
    m2 = speaking("shyam", t)
    char(d, SHYAM, 790, 1600, 2.2, mo=m2, mouth="sad", eyes="half", arms="down", look=-1, lean=-4)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dtext(o, (W / 2, 230), "श्याम का घर", 90, (255, 255, 255), 1.0, stroke=(20, 60, 120))
    if S("L3") + 2.0 < t < E("L3") + 0.5:
        dtext(o, (W / 2, 380), "मायके जा रही हूँ", 70, (255, 120, 120), win(t, S("L3") + 2.0, E("L3") + 0.5, 0.2), stroke=(90, 0, 0), sw=6)
    subtitle(o, t)
    return compose(img, o)

def sc3(t):  # 16.4 - 41.5 chowk
    if t >= 39.4:
        img = Image.new("RGB", (W, H), (20, 20, 30))
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = win(t, 39.4, 41.5, 0.3)
        dtext(o, (W / 2, H / 2 - 40), "दो दिन बाद", 130, (255, 220, 80), a, stroke=(0, 0, 0), font=None)
        dtext(o, (W / 2, H / 2 + 90), "...", 120, (255, 255, 255), a, stroke=(0, 0, 0), font=lfont(120))
        return compose(img, o)
    img = BG["chowk"].copy(); d = ImageDraw.Draw(img)
    shake_t = S("L10") - 0.2
    handshake = shake_t - 1.8 < t < shake_t
    cheer = t >= S("L10")
    mr, ms = speaking("raju", t), speaking("shyam", t)
    gap = 0 if not (handshake or cheer) else 60 * ease((t - (shake_t - 1.8)) / 0.5)
    rx, sx = 320 + gap, 760 - gap
    if t < E("L5") + 0.2: rm, sm = "cry", "sad"
    elif t < E("L9"): rm, sm = "flat", "flat"
    else: rm, sm = "laugh", "laugh"
    if handshake:
        ra, sa = "shake_r", "shake_l"
    elif cheer: ra = sa = "fist_up"
    elif S("L7") <= t <= E("L7"): ra, sa = "point", "cup"
    elif S("L8") <= t <= E("L9"): ra, sa = "cup", "salute"
    else: ra, sa = "cup", "cup"
    char(d, RAJU, rx, 1600, 2.3, mo=mr, mouth=rm, eyes="half" if rm in ("cry", "sad") else ("happy" if cheer else "open"), arms=ra, ph=t, look=1)
    char(d, SHYAM, sx, 1600, 2.3, mo=ms, mouth=sm, eyes="half" if sm == "sad" else ("happy" if cheer else "open"), arms=sa, ph=t, look=-1)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(o)
    if handshake or cheer:
        a = ease((t - (shake_t - 1.8)) / 0.5)
        cx, cy = 540, 1080
        for k in range(12):
            ang = k * math.pi / 6 + t * 0.6
            od.line([(cx + math.cos(ang) * 60, cy + math.sin(ang) * 60), (cx + math.cos(ang) * 200, cy + math.sin(ang) * 200)], fill=(255, 230, 120, int(120 * a)), width=10)
    if S("L8") - 0.1 < t < E("L9") + 0.4:
        dtext(o, (W / 2, 380), "पक्की कसम", 100, (255, 230, 80), win(t, S("L8") - 0.1, E("L9") + 0.4, 0.2), stroke=(130, 30, 0))
    if cheer:
        dtext(o, (W / 2, 330), "दोस्ती ज़िंदाबाद", 96, (255, 255, 255), ease((t - S("L10")) / 0.3), stroke=(0, 100, 40))
        dtext(o, (W / 2, 460), "शराब से आज़ादी", 80, (140, 255, 140), ease((t - S("L10") - 1.2) / 0.3), stroke=(0, 80, 20), sw=7)
    else:
        dtext(o, (W / 2, 230), "गाँव का चौक", 80, (255, 255, 255), 1.0, stroke=(120, 40, 0), sw=6)
    img = compose(img, o)
    if handshake:
        img = zoom(img, 540, 1150, 1 + 0.25 * ease((t - (shake_t - 1.8)) / 1.6))
    o2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); subtitle(o2, t)
    return compose(img, o2)

T4 = 41.5
def sc4(t):  # 41.5 - 53.9 road + theka reveal
    lt = t - T4
    walk_end = 1.8
    cam2 = lerp(300, 1820, ease(lt / walk_end))
    pan = 0
    img, cam = road_view(cam2); d = ImageDraw.Draw(img)
    # uncle at stool
    ux = 2350 - cam
    char(d, UNCLE, ux, 1240, 1.3, pose="sit", mouth="smile", eyes="open", arms="cup", look=-1)
    walking = lt < walk_end
    base = 170
    stopped = not walking
    shock = lt > 2.0
    mr, ms = speaking("raju", t), speaking("shyam", t)
    if not shock: rm = sm = "laugh"
    elif t < S("L13"): rm = sm = "O"
    elif t < S("L15"): rm, sm = "sad", "grin"
    else: rm = sm = "O"
    eyes_r = "big" if shock else "happy"
    eyes_s = "sly" if S("L12") <= t < S("L15") else eyes_r
    char(d, RAJU, base + 0, 1560, 2.0, pose="walk" if walking else "stand", mo=mr, mouth=rm, eyes=eyes_r, arms="down", ph=lt * 9, look=1 if shock else 0)
    char(d, SHYAM, base + 250, 1600, 2.0, pose="walk" if walking else "stand", mo=ms, mouth=sm, eyes=eyes_s, arms="down", ph=lt * 9 + 1, look=1 if shock else 0)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(o)
    if walking:
        for i in range(4):  # music notes
            p = (lt * 0.8 + i * 0.25) % 1
            nx = base + 120 + math.sin(p * 6 + i) * 60; ny = 980 - p * 260
            od.text((nx, ny), "♪", font=lfont(60), fill=(60, 60, 140, int(255 * (1 - p))), anchor="mm")
    warning(o, ease((lt - 1.9) / 0.5))
    if 1.95 < lt < 3.6:
        dtext(o, (W / 2, 330), "दन दन दनननन", 86, (255, 60, 60), win(lt, 1.95, 3.6, 0.15), stroke=(0, 0, 0), sw=7)
    if t >= S("L12") - 0.2:  # thought bubble with dancing bottle above Shyam
        a = ease((t - S("L12") + 0.2) / 0.4)
        bx, by = base + 470, 780
        bubble(o, bx, by, 330, 260, a, [(bx - 110, by + 150, 22), (bx - 150, by + 200, 14)])
        if a > 0.5:
            bot_im, pos = bottle(None, bx, by + math.sin(t * 6) * 10, 1.4, math.sin(t * 5) * 25)
            o.paste(bot_im, pos, bot_im)
    img = compose(img, o)
    z = 1.0
    if 2.2 < lt < 4.0: z = 1 + 0.35 * ease((lt - 2.2) / 1.4)
    elif lt >= 4.0: z = 1.35 - 0.35 * ease((lt - 4.0) / 0.5)
    if t >= S("L15"): z = 1 + 0.3 * ease((t - S("L15")) / 0.4)
    img = zoom(img, base + 130, 1150, z)
    o2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= S("L15"):
        dtext(o2, (W / 2, 330), "समस्या है", 130, (255, 220, 60), ease((t - S("L15")) / 0.2), stroke=(150, 0, 0), sw=10)
    subtitle(o2, t)
    return compose(img, o2)

T5 = 53.9
def sc5(t):  # planning
    img = BG["corner"].copy(); d = ImageDraw.Draw(img)
    # plan drawn on ground
    pa = ease((t - S("L16") - 0.5) / 2.0)
    d.rectangle([380, 1180, 700, 1330], fill=(160, 130, 90))
    d.rectangle([420, 1200, 540, 1260], outline=(255, 255, 255), width=5); d.text((480, 1230), "ठेका", font=dfont(34), anchor="mm", fill=(255, 255, 255))
    if pa > 0:
        d.line([(400, 1310), (400 + 280 * pa, 1310)], fill=(255, 240, 120), width=7)
        if pa > 0.95: d.polygon([(690, 1310), (665, 1295), (665, 1325)], fill=(255, 240, 120))
        d.line([(600, 1200), (660, 1260)], fill=(255, 80, 80), width=6); d.line([(660, 1200), (600, 1260)], fill=(255, 80, 80), width=6)
    mr, ms = speaking("raju", t), speaking("shyam", t)
    beat0, beat1 = E("L19") + 0.1, S("L20") - 0.1   # eyes closed -> half open -> laugh
    if beat0 <= t < beat1:
        bt = (t - beat0) / (beat1 - beat0)
        er = es = "closed" if bt < 0.45 else ("half" if bt < 0.7 else "happy")
        mrr = msm = "flat" if bt < 0.7 else "laugh"
    else:
        er, es = "open", "open"; mrr, msm = "smile", "smile"
        if t >= S("L22"): es, msm, er = "sly", "grin", "sly"
    ra = "salute" if S("L19") <= t <= E("L19") + 0.1 else ("think" if t < S("L19") else "knee")
    sa = "point_l" if S("L16") <= t <= E("L18") else ("think" if S("L20") <= t < S("L22") else "knee")
    char(d, RAJU, 250, 1620, 2.2, pose="sit", mo=mr, mouth=mrr, eyes=er, arms=ra if ra != "knee" else "knee", look=1)
    char(d, SHYAM, 830, 1620, 2.2, pose="sit", mo=ms, mouth=msm, eyes=es, arms=sa, look=-1)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dtext(o, (W / 2, 220), "सीक्रेट प्लान", 100, (255, 255, 255), ease((t - T5) / 0.4), stroke=(20, 40, 100))
    if S("L19") <= t <= E("L19") + 0.3:
        dtext(o, (W / 2, 370), "आँखें बंद  तेज़ भागो", 76, (255, 230, 80), 1.0, stroke=(100, 30, 0), sw=6)
    if t >= S("L22") + 1.0:
        dtext(o, (W / 2, 370), "बस सूंघना", 100, (255, 200, 80), ease((t - S("L22") - 1.0) / 0.3), stroke=(120, 30, 0))
    subtitle(o, t)
    return compose(img, o)

T6 = 80.8
RUN0, RUN1 = E("L26"), S("L27") - 0.3
def sc6(t):
    lt = t - T6
    running = RUN0 <= t < RUN1
    if t < RUN0:
        img, cam = road_view(2000); d = ImageDraw.Draw(img)
        char(d, UNCLE, 2350 - cam, 1240, 1.3, pose="sit", mouth="smile", arms="cup", look=-1)
        mr, ms = speaking("raju", t), speaking("shyam", t)
        char(d, RAJU, 330, 1580, 2.1, mo=mr, mouth="flat", eyes="closed", arms="down")
        char(d, SHYAM, 640, 1580, 2.1, mo=ms, mouth="flat", eyes="closed", arms="down")
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); warning(o)
        if t >= S("L26"):
            k = int((t - S("L26")) / ((E("L26") - S("L26")) / 4))
            txt = ["1", "2", "3", "भागो"][min(3, k)]
            dtext(o, (W / 2, 520), txt, 220 if k < 3 else 160, (255, 230, 60), 1.0, stroke=(150, 0, 0), sw=12, font=lfont(220) if k < 3 else None)
        subtitle(o, t)
        return compose(img, o)
    if running:
        rt = t - RUN0
        slow = 1.0
        sm0 = 3.6  # slow motion from here
        if rt > sm0: eff = sm0 + (rt - sm0) * 0.35
        else: eff = rt
        cam = 2000 - eff * 520
        img, cam = road_view(cam); d = ImageDraw.Draw(img)
        # rickshaw at world x 1300
        rkx = 1300 - cam
        hit = eff > 1.55
        d.ellipse([rkx - 150, 1420, rkx - 30, 1540], outline=(40, 40, 40), width=10)
        d.ellipse([rkx + 60, 1420, rkx + 180, 1540], outline=(40, 40, 40), width=10)
        d.rectangle([rkx - 60, 1220, rkx + 170, 1400], fill=(40, 120, 200), outline=(20, 60, 120), width=5)
        d.polygon([(rkx - 80, 1220), (rkx + 190, 1220), (rkx + 160, 1150), (rkx - 50, 1150)], fill=(230, 60, 60))
        char(d, dict(SHYAM, kurta=(200, 200, 200), bottom=(80, 80, 80), hair="messy", mus=1), rkx - 100, 1440, 1.4, mouth="O" if hit else "smile", eyes="big" if hit else "open", arms="down")
        # dog at world x running left faster
        dgx = 1050 - cam - max(0, eff - 2.0) * 700
        if -200 < dgx < W + 200:
            d.ellipse([dgx - 70, 1480, dgx + 70, 1540], fill=(170, 120, 70)); d.ellipse([dgx - 110, 1450, dgx - 50, 1500], fill=(170, 120, 70))
            for k in range(4): d.line([(dgx - 50 + k * 30, 1530), (dgx - 50 + k * 30 + math.sin(t * 20 + k) * 12, 1575)], fill=(150, 100, 60), width=10)
            d.polygon([(dgx - 100, 1455), (dgx - 90, 1425), (dgx - 80, 1455)], fill=(140, 90, 50))
        # runners (world positions follow camera; raju bumps into rickshaw)
        rjx = 330 + (60 * math.sin(eff * 30) * clamp(1 - (eff - 1.55) / 0.6) if hit else 0)
        if hit and eff < 2.2: rjx = rkx + 220 + (eff - 1.55) * 120
        char(d, RAJU, rjx, 1600, 2.0, pose="run", mouth="O", eyes="closed", arms="run", ph=eff * 16, lean=-12)
        char(d, SHYAM, 680, 1620, 2.0, pose="run", mouth="O", eyes="closed", arms="run", ph=eff * 16 + 1.5, lean=-12)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); warning(o)
        if 1.5 < eff < 2.4:
            dtext(o, (W / 2, 1000), "धड़ाम", 130, (255, 230, 80), win(eff, 1.5, 2.4, 0.1), stroke=(150, 30, 0), sw=10)
            od = ImageDraw.Draw(o)
            for k in range(5):
                ang = eff * 8 + k * 1.25; sx2, sy2 = rjx + math.cos(ang) * 90, 1040 + math.sin(ang) * 30
                od.text((sx2, sy2), "★", font=lfont(46), anchor="mm", fill=(255, 220, 40, 255))
        if 2.0 < eff < 3.4:
            dtext(o, (dgx - 40, 1350), "भौं भौं", 64, (255, 255, 255), win(eff, 2.0, 3.4, 0.15), stroke=(0, 0, 0), sw=6)
        if rt > sm0:
            dtext(o, (W / 2, 300), "स्लो मोशन", 70, (255, 255, 255), ease((rt - sm0) / 0.3), stroke=(0, 0, 0), sw=6)
        dtext(o, (W / 2, 180), "भागो", 110, (255, 80, 60), 1.0 if rt < sm0 else 0.5, stroke=(0, 0, 0), sw=9)
        return compose(img, o)
    # uncle laughing close-up
    img, cam = road_view(2050); d = ImageDraw.Draw(img)
    mu = speaking("uncle", t)
    char(d, UNCLE, 2350 - cam + 120, 1500, 2.4, pose="sit", mo=mu, mouth="laugh", eyes="happy", arms="cup", look=-1)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); warning(o)
    od = ImageDraw.Draw(o)
    for k in range(3):
        p = (t * 0.9 + k * 0.33) % 1
        od.text((780 + k * 40, 900 - p * 200), "हा", font=dfont(60), anchor="mm", fill=(255, 255, 255, int(255 * (1 - p))), stroke_width=4, stroke_fill=(0, 0, 0, int(255 * (1 - p))))
    subtitle(o, t)
    return compose(img, o)

T7 = 95.5
DANCE0, DANCE1 = E("L30"), E("L30") + 2.2
SIT0 = DANCE1 + 0.3
UP = E("L34") + 0.2
def sc7(t):
    img = BG["field"].copy(); d = ImageDraw.Draw(img)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(o)
    mr, ms = speaking("raju", t), speaking("shyam", t)
    if t < S("L30") - 0.2:
        hugging = t > S("L28") - 1.2 and t < S("L28") + 0.4
        a1, a2 = ("hug_r", "hug_l") if hugging else ("fist_up", "fist_up")
        gx = 80 if hugging else 0
        char(d, RAJU, 360 + gx, 1640, 2.3, mo=mr, mouth="laugh", eyes="happy", arms=a1, look=1)
        char(d, SHYAM, 720 - gx, 1640, 2.3, mo=ms, mouth="laugh", eyes="happy", arms=a2, look=-1)
        sweat(d, 360 + gx, 900, 2.3, t)
    elif t < SIT0:
        ph = t * 7
        char(d, RAJU, 330 + math.sin(ph) * 30, 1640 - abs(math.sin(ph)) * 40, 2.2, mo=mr, mouth="laugh", eyes="happy", arms="dance", ph=ph, pose="walk")
        char(d, SHYAM, 750 - math.sin(ph) * 30, 1640 - abs(math.cos(ph)) * 40, 2.2, mo=ms, mouth="laugh", eyes="happy", arms="dance", ph=ph + 1.5, pose="walk")
        # fireworks
        for k in range(5):
            st = S("L30") - 0.2 + k * 0.6
            p = (t - st) / 1.4
            if 0 <= p <= 1:
                cx, cy = 180 + k * 180, 300 + (k % 2) * 160
                col = [(255, 80, 80), (255, 220, 60), (120, 220, 255), (180, 120, 255), (120, 255, 140)][k]
                for j in range(14):
                    ang = j * math.pi / 7
                    r = 30 + p * 170
                    od.ellipse([cx + math.cos(ang) * r - 6, cy + math.sin(ang) * r + p * 40 - 6, cx + math.cos(ang) * r + 6, cy + math.sin(ang) * r + p * 40 + 6], fill=col + (int(255 * (1 - p)),))
        dtext(o, (W / 2, 1000), "हम जीत गए", 110, (255, 230, 80), 1.0, stroke=(120, 20, 0))
    else:
        rising = t > UP
        if rising:
            pr = ease((t - UP) / 0.8)
            char(d, RAJU, 330, 1640, 2.2, mouth="grin", eyes="sly", arms="down", look=1)
            char(d, SHYAM, 750, 1640, 2.2, mouth="grin", eyes="sly", arms="down", look=-1)
        else:
            silence = t < S("L31")
            char(d, RAJU, 330, 1640, 2.2, pose="sit", mo=mr, mouth="flat", eyes="half" if silence else ("sly" if t >= S("L33") else "open"), arms="knee", look=1)
            char(d, SHYAM, 750, 1640, 2.2, pose="sit", mo=ms, mouth="flat" if t < S("L34") else "grin", eyes="half" if silence else ("big" if t >= S("L34") else "open"), arms="knee", look=-1)
            sweat(d, 330, 1180, 2.2, t); sweat(d, 750, 1180, 2.2, t + 0.3)
            if silence:
                dtext(o, (W / 2, 900), "...", 120, (255, 255, 255), win(t, SIT0, S("L31"), 0.3), stroke=(0, 0, 0), font=lfont(120))
            if t >= S("L34"):
                for k in (-1, 1):  # sparkle eyes
                    od.text((750 + k * 24, 1095), "✦", font=lfont(34), anchor="mm", fill=(255, 240, 120, 255))
            if t >= S("L33") + 1.5:
                dtext(o, (W / 2, 330), "एक पैक तो बनता है", 90, (255, 220, 80), ease((t - S("L33") - 1.5) / 0.3), stroke=(120, 20, 0))
    subtitle(o, t)
    return compose(img, o)

T8 = UP + 0.8
DOOR0 = T8 + 2.6
def sc8(t):  # walk to theka from behind, door, black, narration
    lt = t - T8
    if t < DOOR0 + 1.5:
        img, cam = road_view(2200 - 120); d = ImageDraw.Draw(img)
        p = ease(lt / 2.6)
        doorx = 2200 + 535 - cam
        dop = clamp((t - DOOR0 + 0.6) / 0.4) if t < DOOR0 + 0.5 else clamp(1 - (t - DOOR0 - 0.5) / 0.3)
        d.rectangle([doorx - 65, 820, doorx + 65, 1250], fill=(30, 20, 10))
        d.rectangle([doorx - 65, 820, doorx - 65 + 130 * (1 - dop), 1250], fill=(100, 60, 30), outline=(50, 30, 15), width=5)
        if t < DOOR0 + 0.2:
            s = lerp(2.0, 1.0, p); y = lerp(1700, 1260, p)
            for k, P in ((-1, RAJU), (1, SHYAM)):
                x = lerp(540 + k * 160, doorx + k * 30, p)
                char(d, P, x, y, s, pose="walk", mouth="grin", eyes="sly", arms="down", ph=lt * 9 + (k > 0) * 1.5)
                # cover face (view from behind): draw hair over head
                hr = 27 * s; hy = y - 70 * s - 62 * s - hr - 6 * s
                d.ellipse([x - hr, hy - hr, x + hr, hy + hr], fill=(30, 25, 20))
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); warning(o)
        img = compose(img, o)
        fade = clamp((t - DOOR0 - 0.6) / 0.8)
        return Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), fade)
    img = Image.new("RGB", (W, H), (0, 0, 0)); o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= S("L35"):
        dtext(o, (W / 2, 820), "कसम तोड़ी नहीं", 92, (255, 255, 255), ease((t - S("L35") - 1.5) / 0.4), stroke=(0, 0, 0))
        dtext(o, (W / 2, 960), "बस जश्न मनाया", 104, (255, 220, 70), ease((t - S("L35") - 3.4) / 0.4), stroke=(0, 0, 0))
    subtitle(o, t)
    return compose(img, o)

MORAL0 = E("L35") + 0.4
ENDC = MORAL0 + 5.0
def sc9(t):
    if t < ENDC:
        img = vgrad((30, 30, 60), (90, 30, 60)); o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = ease((t - MORAL0) / 0.5)
        od = ImageDraw.Draw(o)
        od.rounded_rectangle([60, 560, W - 60, 1340], radius=40, fill=(255, 255, 255, int(235 * a)))
        dtext(o, (W / 2, 660), "कहानी की सीख", 84, (200, 40, 60), a, stroke=(255, 255, 255), sw=2)
        lines = ["दोस्ती और शराब", "दोनों की कसम", "एक जैसी होती है", "टूटने के लिए ही बनी है"]
        for i, l in enumerate(lines):
            dtext(o, (W / 2, 800 + i * 120), l, 72, (40, 30, 30), ease((t - MORAL0 - 0.4 - i * 0.5) / 0.4), stroke=(255, 255, 255), sw=2)
        dtext(o, (W / 2, 1480), "हा हा हा", 90, (255, 220, 80), ease((t - MORAL0 - 2.6) / 0.4), stroke=(0, 0, 0))
        warning(o)
        return compose(img, o)
    lt = t - ENDC
    img = vgrad((255, 140, 50), (220, 40, 80)); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(o)
    btns = [("LIKE", (40, 120, 230)), ("SHARE", (40, 170, 90)), ("SUBSCRIBE", (230, 30, 30))]
    for i, (txt, col) in enumerate(btns):
        a = ease((lt - i * 0.35) / 0.3)
        sc = 0.6 + 0.4 * a + (0.08 * math.sin(lt * 8) if i == 2 else 0)
        w, h = 620 * sc, 150 * sc; y = 650 + i * 230
        od.rounded_rectangle([W / 2 - w / 2, y - h / 2, W / 2 + w / 2, y + h / 2], radius=int(h / 2), fill=col + (int(255 * a),))
        od.text((W / 2, y), txt, font=lfont(int(70 * sc)), anchor="mm", fill=(255, 255, 255, int(255 * a)))
    dtext(o, (W / 2, 1400), "जय छठी मैया", 80, (255, 240, 150), ease((lt - 1.4) / 0.4), stroke=(120, 20, 0), sw=6)
    img = compose(img, o)
    return Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), clamp((lt - (DUR - ENDC - 0.8)) / 0.8))

SC = [(0, 9.3, sc1), (9.3, 16.4, sc2), (16.4, 41.5, sc3), (41.5, 53.9, sc4), (53.9, 80.8, sc5), (80.8, T7, sc6), (T7, T8, sc7), (T8, MORAL0, sc8), (MORAL0, 9999, sc9)]
def frame(i):
    t = i / FPS
    for a, b, f in SC:
        if a <= t < b: return f(t)
    return sc9(DUR - 0.01)

# ---------- audio: music + sfx ----------
def build_audio(path):
    dlg, sr = sf.read("/home/claude/tts/dialog.wav", dtype="float32")
    n = len(dlg); mus = np.zeros(n, dtype=np.float32); sfx = np.zeros(n, dtype=np.float32)
    def put(buf, t0, x):
        s = int(t0 * sr)
        if s >= n: return
        e = min(n, s + len(x)); buf[s:e] += x[:e - s]
    def tone(f, dur, vol, decay=3, kind="sine", vib=0):
        tt = np.arange(int(sr * dur)) / sr
        ph = 2 * np.pi * f * tt + (vib * np.sin(2 * np.pi * 5 * tt) if vib else 0)
        if kind == "saw": w = 2 * ((f * tt) % 1) - 1
        elif kind == "sq": w = np.sign(np.sin(ph))
        else: w = np.sin(ph) + 0.3 * np.sin(2 * ph)
        env = np.minimum(1, tt * 60) * np.exp(-tt * decay)
        return (w * env * vol).astype(np.float32)
    def noise(dur, vol, decay=10):
        tt = np.arange(int(sr * dur)) / sr
        return (np.random.uniform(-1, 1, len(tt)) * np.exp(-tt * decay) * vol).astype(np.float32)
    np.random.seed(1)
    # comic chase music 0-6.6 (tuba bounce + fast melody)
    k = 0; t0 = 0
    while t0 < 6.6:
        put(mus, t0, tone([98, 147][k % 2], 0.22, 0.25, 8, "sq"));
        if k % 2 == 0: put(mus, t0, tone([392, 440, 494, 523, 494, 440, 392, 349][(k // 2) % 8], 0.18, 0.08, 6, "sq"))
        k += 1; t0 += 0.18
    for t1 in np.arange(0.3, 6.5, 0.9): put(sfx, t1, noise(0.12, 0.25, 30))  # broom whacks
    put(sfx, 6.9, noise(0.35, 0.6, 9)); put(sfx, 6.9, tone(70, 0.4, 0.5, 7))  # door slam
    # scene 2 nagging drum
    for t1 in np.arange(9.3, 16.2, 0.5): put(mus, t1, tone(110, 0.2, 0.15, 10))
    # scene 3: sad flute then emotional
    fl = [587, 523, 494, 440, 494, 523, 440, 392]
    for i, t1 in enumerate(np.arange(16.6, 33.5, 0.85)): put(mus, t1, tone(fl[i % 8], 0.9, 0.06, 1.5, vib=0.4))
    for i, t1 in enumerate(np.arange(S("L10") - 2.2, 39.2, 0.5)): put(mus, t1, tone([262, 330, 392, 523][i % 4], 0.6, 0.09, 2))
    # 2 din baad whoosh
    put(sfx, 39.5, tone(300, 1.2, 0.12, 2, vib=6))
    # walking happy whistle
    for i, t1 in enumerate(np.arange(41.6, 43.3, 0.22)): put(mus, t1, tone([784, 880, 988, 880][i % 4], 0.2, 0.07, 6))
    # DUN DUN DUNNN
    dd = T4 + 1.95
    put(sfx, dd, tone(147, 0.35, 0.35, 3, "saw")); put(sfx, dd + 0.4, tone(139, 0.35, 0.35, 3, "saw")); put(sfx, dd + 0.8, tone(117, 1.6, 0.4, 1.2, "saw"))
    put(sfx, S("L12"), tone(1320, 0.6, 0.06, 4)); put(sfx, S("L12") + 0.2, tone(1760, 0.6, 0.06, 4))
    put(sfx, S("L15"), tone(110, 0.8, 0.35, 3, "saw"))
    # planning: sneaky pizzicato
    for i, t1 in enumerate(np.arange(54.0, 80.6, 0.3)):
        put(mus, t1, tone([196, 0, 233, 0, 262, 0, 233, 196][i % 8] or 1, 0.12, 0.10 if i % 2 == 0 else 0, 14))
    # rocky fanfare during run
    fan = [(392, .3), (494, .3), (587, .6), (523, .3), (587, .9)]
    tt0 = S("L24") - 1.4
    while tt0 < RUN1 + 0.2:
        for f, du in fan:
            put(mus, tt0, tone(f, du, 0.09, 1.5, "saw")); put(mus, tt0, tone(f / 2, du, 0.06, 1.5, "saw")); tt0 += du
    for i, t1 in enumerate([S("L26") + j * (E("L26") - S("L26")) / 4 for j in range(3)]): put(sfx, t1, tone(880, 0.15, 0.15, 10))
    rk = RUN0 + 1.55
    put(sfx, rk, noise(0.4, 0.5, 8)); put(sfx, rk + 0.05, tone(2200, 0.5, 0.08, 6)); put(sfx, rk + 0.3, tone(2600, 0.4, 0.06, 6))
    for b in (RUN0 + 2.1, RUN0 + 2.5): put(sfx, b, noise(0.12, 0.3, 25) * 1.0); put(sfx, b, tone(330, 0.12, 0.2, 20, "sq"))
    # uncle laugh bed
    for t1 in np.arange(S("L27"), E("L27"), 0.4): put(mus, t1, tone(147, 0.2, 0.08, 10))
    # victory + fireworks
    for i, t1 in enumerate(np.arange(S("L28") - 0.5, DANCE1, 0.25)): put(mus, t1, tone([523, 659, 784, 1047, 784, 659][i % 6], 0.25, 0.07, 5))
    for k in range(6): put(sfx, S("L30") - 0.2 + k * 0.6, noise(0.6, 0.35, 6))
    # crickets in silence
    for t1 in np.arange(SIT0 + 0.3, S("L31") - 0.1, 0.35): put(sfx, t1, tone(4200, 0.08, 0.03, 20))
    # sneaky again then door creak + slam
    for i, t1 in enumerate(np.arange(S("L33"), DOOR0, 0.3)): put(mus, t1, tone([196, 233, 262, 233][i % 4], 0.12, 0.09, 14))
    put(sfx, DOOR0 - 0.6, tone(180, 0.6, 0.06, 1, "saw", vib=8)); put(sfx, DOOR0 + 0.5, noise(0.3, 0.5, 10)); put(sfx, DOOR0 + 0.5, tone(70, 0.4, 0.4, 7))
    # moral comic + end
    for i, t1 in enumerate(np.arange(MORAL0, DUR - 1, 0.3)): put(mus, t1, tone([262, 330, 392, 330][i % 4], 0.25, 0.08, 6))
    put(sfx, ENDC, tone(1568, 0.6, 0.1, 4)); put(sfx, ENDC + 0.35, tone(2093, 0.6, 0.1, 4))
    env = np.convolve((np.abs(dlg) > 0.02).astype(np.float32), np.ones(int(sr * 0.25), dtype=np.float32) / (sr * 0.25), mode="same")
    duck = 1 - 0.6 * np.clip(env * 3, 0, 1)
    out = dlg * 1.0 + mus * duck + sfx * 0.9
    out = np.clip(out / max(1.0, np.max(np.abs(out)) / 0.97), -1, 1)
    sf.write(path, out, sr)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        secs = [float(x) for x in sys.argv[2].split(",")]
        ims = [frame(int(s * FPS)).resize((270, 480)) for s in secs]
        cols = 7; rows = (len(ims) + cols - 1) // cols
        g = Image.new("RGB", (270 * cols, 480 * rows))
        for i, im in enumerate(ims): g.paste(im, ((i % cols) * 270, (i // cols) * 480))
        g.save("/home/claude/tts/rs_grid.png"); sys.exit()
    wav = "/home/claude/tts/rs_mix.wav"; build_audio(wav)
    N = int(DUR * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT], stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait(); print("done", DUR)
