import math, subprocess, sys, json, random
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "/home/claude/tts")
import raju_shyam as R

W, H, FPS = 1080, 1920, 24
VJ = json.load(open("/home/claude/dhanteras/vo.json")); SEGS = VJ["segs"]; DUR = VJ["total"]; SEG = {s["id"]: s for s in SEGS}
OUT = "/home/claude/dhanteras_2026.mp4"
dfont, ease, clamp, lerp = R.dfont, R.ease, R.clamp, R.lerp
S = lambda i: SEG[i]["start"]; E = lambda i: SEG[i]["end"]
GOLD, CREAM, MAR = (255, 205, 60), (255, 244, 214), (70, 8, 18)

def at(i, word):  # time a word is spoken inside segment i (by character position)
    s = SEG[i]; p = s["text"].find(word) / max(1, len(s["text"]))
    return s["start"] + (s["end"] - s["start"]) * p

# ---------- static background ----------
def make_bg():
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(110 - 50 * t), int(12 + 4 * t), int(30 + 4 * t)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    cols = [(255, 140, 20), (230, 40, 90), (255, 200, 40), (60, 170, 90)]
    for cx, cy in ((0, H), (W, H), (0, 330), (W, 330)):
        for ring, rr in enumerate([300, 230, 160, 95]):
            n = 18 if ring % 2 == 0 else 12
            for k in range(n):
                a = 2 * math.pi * k / n + ring * .3
                px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr; pr = rr * .2
                od.ellipse([px - pr, py - pr * .55, px + pr, py + pr * .55], fill=cols[ring % 4] + (60,))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    # marigold toran
    for k in range(0, W + 40, 40):
        yy = 40 + 34 * abs(math.sin(k / W * math.pi * 4))
        d.line([(k, 0), (k, yy - 16)], fill=(60, 120, 40), width=3)
        d.ellipse([k - 20, yy - 20, k + 20, yy + 20], fill=(255, 150, 20) if (k // 40) % 2 else (255, 195, 30))
        d.ellipse([k - 8, yy - 8, k + 8, yy + 8], fill=(220, 100, 10))
    # brand pill
    d.rounded_rectangle([W / 2 - 230, 120, W / 2 + 230, 200], radius=40, fill=MAR, outline=GOLD, width=4)
    d.text((W / 2, 160), "भारत के त्योहार", font=dfont(50), anchor="mm", fill=GOLD)
    return img
BG = make_bg()
random.seed(3)
SPARK = [(random.uniform(0, W), random.uniform(0, H), random.uniform(.3, 1), random.uniform(0, 6)) for _ in range(55)]

def txt(od, xy, s, size, col=CREAM, a=1.0, sw=8, stroke=MAR, anchor="mm"):
    if a <= 0: return
    od.text(xy, s, font=dfont(size), anchor=anchor, fill=col + (int(255 * a),), stroke_width=sw, stroke_fill=stroke + (int(255 * a),))

def glow(o, cx, cy, r, a, col=(255, 190, 60)):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (int(150 * a),))
    o.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * .45)))

def flame(od, x, y, s, t, a=1.0):
    fl = 1 + .08 * math.sin(t * 17 + x)
    h = 70 * s * fl; w = 24 * s
    od.polygon([(x, y - h), (x + w, y - h * .45), (x + w * .6, y - 6 * s), (x, y), (x - w * .6, y - 6 * s), (x - w, y - h * .45)], fill=(255, 150, 20, int(255 * a)))
    od.polygon([(x, y - h * .72), (x + w * .5, y - h * .38), (x, y - 8 * s), (x - w * .5, y - h * .38)], fill=(255, 245, 160, int(255 * a)))

def diya(od, x, y, s, t, a=1.0, flames=1):
    c = (200, 80, 25, int(255 * a))
    od.chord([x - 110 * s, y - 70 * s, x + 110 * s, y + 70 * s], 0, 180, fill=c)
    od.rectangle([x - 110 * s, y - 5 * s, x + 110 * s, y + 5 * s], fill=(245, 170, 50, int(255 * a)))
    for k in range(-2, 3):
        od.ellipse([x + k * 34 * s - 6 * s, y + 26 * s - 6 * s, x + k * 34 * s + 6 * s, y + 26 * s + 6 * s], fill=(255, 215, 90, int(255 * a)))
    if flames == 1: flame(od, x, y - 4 * s, s, t, a)
    else:
        for fx in (-80, -27, 27, 80): flame(od, x + fx * s, y - 4 * s, s * .7, t + fx, a)

# ---------- icons ----------
def coin(od, x, y, s, a):
    od.ellipse([x - 60 * s, y - 60 * s, x + 60 * s, y + 60 * s], fill=(235, 175, 30, int(255 * a)), outline=(160, 100, 10, int(255 * a)), width=int(6 * s))
    od.ellipse([x - 40 * s, y - 40 * s, x + 40 * s, y + 40 * s], outline=(255, 225, 110, int(255 * a)), width=int(5 * s))
    od.ellipse([x + 15 * s, y - 70 * s, x + 105 * s, y + 20 * s], fill=(200, 205, 215, int(255 * a)), outline=(140, 145, 160, int(255 * a)), width=int(5 * s))

def kalash(od, x, y, s, a, col=(205, 140, 50)):
    c = col + (int(255 * a),)
    od.ellipse([x - 70 * s, y - 55 * s, x + 70 * s, y + 70 * s], fill=c)
    od.rectangle([x - 30 * s, y - 85 * s, x + 30 * s, y - 45 * s], fill=c)
    od.ellipse([x - 48 * s, y - 100 * s, x + 48 * s, y - 75 * s], fill=c)
    od.line([(x - 55 * s, y), (x + 55 * s, y)], fill=(255, 220, 120, int(255 * a)), width=int(6 * s))

def broom(od, x, y, s, a):
    od.rounded_rectangle([x - 10 * s, y - 100 * s, x + 10 * s, y - 10 * s], radius=6, fill=(200, 60, 40, int(255 * a)))
    for k in range(-8, 9):
        od.line([(x + k * 3 * s, y - 15 * s), (x + k * 7 * s, y + 85 * s)], fill=(215, 180, 90, int(255 * a)), width=int(4 * s))

def dhaniya(od, x, y, s, a):
    od.chord([x - 75 * s, y - 30 * s, x + 75 * s, y + 60 * s], 0, 180, fill=(150, 90, 40, int(255 * a)))
    rr = random.Random(5)
    for _ in range(26):
        px, py = x + rr.uniform(-60, 60) * s, y + rr.uniform(-28, 12) * s
        od.ellipse([px - 9 * s, py - 9 * s, px + 9 * s, py + 9 * s], fill=(195, 160, 80, int(255 * a)), outline=(140, 110, 50, int(255 * a)))

def knife(od, x, y, s, a):
    od.polygon([(x - 80 * s, y + 10 * s), (x + 50 * s, y - 40 * s), (x + 60 * s, y - 20 * s), (x - 70 * s, y + 25 * s)], fill=(190, 195, 205, int(255 * a)))
    od.rounded_rectangle([x + 45 * s, y - 45 * s, x + 110 * s, y - 15 * s], radius=10, fill=(40, 40, 45, int(255 * a)))
    for dx in (-20, 20):
        od.ellipse([x + dx * s - 22 * s, y + 35 * s, x + dx * s + 22 * s, y + 79 * s], outline=(60, 60, 70, int(255 * a)), width=int(7 * s))

def glass(od, x, y, s, a):
    od.polygon([(x - 50 * s, y - 80 * s), (x + 50 * s, y - 80 * s), (x + 38 * s, y + 70 * s), (x - 38 * s, y + 70 * s)], fill=(180, 220, 240, int(130 * a)), outline=(230, 250, 255, int(255 * a)))
    od.line([(x - 10 * s, y - 60 * s), (x + 15 * s, y - 10 * s), (x - 5 * s, y + 30 * s)], fill=(255, 255, 255, int(255 * a)), width=int(4 * s))

def empty_pot(od, x, y, s, a):
    kalash(od, x, y, s, a, col=(110, 110, 120))
    od.ellipse([x - 40 * s, y - 97 * s, x + 40 * s, y - 80 * s], fill=(30, 30, 35, int(255 * a)))

def mark(od, x, y, ok, a):
    c = (40, 170, 70) if ok else (220, 40, 40)
    od.ellipse([x - 34, y - 34, x + 34, y + 34], fill=c + (int(255 * a),), outline=(255, 255, 255, int(255 * a)), width=4)
    if ok: od.line([(x - 16, y), (x - 4, y + 13), (x + 17, y - 12)], fill=(255, 255, 255, int(255 * a)), width=8)
    else:
        od.line([(x - 13, y - 13), (x + 13, y + 13)], fill=(255, 255, 255, int(255 * a)), width=8)
        od.line([(x - 13, y + 13), (x + 13, y - 13)], fill=(255, 255, 255, int(255 * a)), width=8)

def item_grid(od, t, items, ok, title, t0, t1):
    a0 = ease((t - t0 + .15) / .35) * ease((t1 - t) / .3)
    if a0 <= 0: return
    col = (90, 220, 120) if ok else (255, 90, 90)
    txt(od, (W / 2, 420), title, 108, col, a0, sw=10)
    pos = [(290, 760), (790, 760), (290, 1190), (790, 1190)]
    for k, (tk, fn, lab) in enumerate(items):
        p = ease((t - tk) / .35); a = p * a0
        if a <= 0: continue
        x, y = pos[k]; sc = .6 + .4 * p
        od.rounded_rectangle([x - 230, y - 190, x + 230, y + 190], radius=40, fill=(255, 245, 225, int(235 * a)), outline=col + (int(255 * a),), width=6)
        fn(od, x, y - 40, 1.25 * sc, a)
        txt(od, (x, y + 130), lab, 56, MAR, a, sw=0)
        mark(od, x + 195, y - 155, ok, a)

def subtitle(od, t):
    for s in SEGS:
        if s["start"] - .05 <= t <= s["end"] + .25:
            words = R.clean(s["text"]).split(); f = dfont(60)
            lines, cur = [], []
            for w in words:
                if od.textlength(" ".join(cur + [w]), font=f) > W - 160 and cur: lines.append(cur); cur = [w]
                else: cur.append(w)
            lines.append(cur)
            y = 1640 - (len(lines) - 1) * 40
            od.rounded_rectangle([50, y - 55, W - 50, y + (len(lines) - 1) * 80 + 55], radius=30, fill=(0, 0, 0, 140))
            for ln in lines:
                txt(od, (W / 2, y), " ".join(ln), 60, (255, 255, 255), 1, sw=5, stroke=(0, 0, 0)); y += 80

def frame(i):
    t = i / FPS
    img = BG.copy().convert("RGBA")
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(o)
    for x, y, s, ph in SPARK:
        yy = (y - t * 40 * s) % H; a = .5 + .5 * math.sin(t * 3 + ph)
        od.ellipse([x - 4 * s, yy - 4 * s, x + 4 * s, yy + 4 * s], fill=(255, 220, 120, int(200 * a * s)))
    # S1: hook title
    a = ease(t / .3) * ease((S("s2") + .4 - t) / .3)
    if a > 0:
        z = 1 + .15 * ease(t / 1.0)
        glow(o, W / 2, 900, 380, a)
        diya(od, W / 2, 1180, 1.6, t, a)
        txt(od, (W / 2, 640), "धनतेरस", int(190 * z), GOLD, a, sw=12)
        txt(od, (W / 2, 830), "२०२६", int(150 * z), CREAM, a, sw=10)
        q = ease((t - .9) / .3) * a
        txt(od, (W / 2, 1400), "कब है", 120, (255, 255, 255), q, sw=10)
    # S2: date card
    a = ease((t - S("s2") - .1) / .3) * ease((S("s3") - t) / .3)
    if a > 0:
        p = ease((t - S("s2")) / .4); y0 = lerp(1100, 560, p)
        od.rounded_rectangle([W / 2 - 330, y0, W / 2 + 330, y0 + 640], radius=50, fill=(255, 248, 235, int(255 * a)))
        od.rounded_rectangle([W / 2 - 330, y0, W / 2 + 330, y0 + 170], radius=50, fill=(200, 30, 50, int(255 * a)))
        od.rectangle([W / 2 - 330, y0 + 120, W / 2 + 330, y0 + 170], fill=(200, 30, 50, int(255 * a)))
        txt(od, (W / 2, y0 + 85), "नवंबर २०२६", 84, (255, 255, 255), a, sw=0)
        txt(od, (W / 2, y0 + 360), "६", 330, (200, 30, 50), a, sw=0)
        txt(od, (W / 2, y0 + 570), "शुक्रवार", 92, MAR, a, sw=0)
        for rx in (-200, 200): od.ellipse([W / 2 + rx - 22, y0 - 22, W / 2 + rx + 22, y0 + 22], fill=(120, 120, 130, int(255 * a)))
    # S3: muhurat
    a = ease((t - S("s3")) / .3) * ease((S("s4") - t) / .3)
    if a > 0:
        txt(od, (W / 2, 420), "शुभ मुहूर्त", 120, GOLD, a, sw=10)
        cx, cy = W / 2, 800
        od.ellipse([cx - 210, cy - 210, cx + 210, cy + 210], fill=(255, 248, 235, int(255 * a)), outline=GOLD + (int(255 * a),), width=12)
        for k in range(12):
            an = k * math.pi / 6
            od.line([(cx + math.sin(an) * 175, cy - math.cos(an) * 175), (cx + math.sin(an) * 195, cy - math.cos(an) * 195)], fill=MAR + (int(255 * a),), width=6)
        sweep = ease((t - S("s3")) / 3)
        ha = math.radians(lerp(180, 240, sweep)); ma = sweep * 4 * math.pi
        od.line([(cx, cy), (cx + math.sin(ha) * 110, cy - math.cos(ha) * 110)], fill=MAR + (int(255 * a),), width=14)
        od.line([(cx, cy), (cx + math.sin(ma) * 160, cy - math.cos(ma) * 160)], fill=(200, 30, 50, int(255 * a)), width=8)
        od.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=MAR + (int(255 * a),))
        b = ease((t - at("s3", "प्रदोष")) / .3) * a
        od.rounded_rectangle([110, 1060, W - 110, 1300], radius=40, fill=MAR + (int(230 * b),), outline=GOLD + (int(255 * b),), width=5)
        txt(od, (W / 2, 1120), "प्रदोष काल", 72, GOLD, b, sw=0)
        txt(od, (W / 2, 1225), "शाम लगभग ६ से ८ बजे", 84, (255, 255, 255), b, sw=0)
        c = ease((t - at("s3", "अपने")) / .3) * a
        txt(od, (W / 2, 1400), "अपने शहर का पंचांग ज़रूर देखें", 58, CREAM, c, sw=5)
    # S4 / S5
    item_grid(od, t, [(at("s4", "सोना"), coin, "सोना चाँदी"), (at("s4", "पीतल"), kalash, "पीतल तांबा"),
                      (at("s4", "झाड़ू"), broom, "नई झाड़ू"), (at("s4", "साबुत"), dhaniya, "साबुत धनिया")], True, "क्या खरीदें", S("s4"), S("s5"))
    item_grid(od, t, [(at("s5", "लोहे"), knife, "लोहा चाकू कैंची"), (at("s5", "काँच"), glass, "काँच"),
                      (at("s5", "खाली"), empty_pot, "खाली बर्तन")], False, "क्या न खरीदें", S("s5"), S("s6"))
    # S6: yama deepdaan
    a = ease((t - S("s6")) / .3) * ease((S("s7") - t) / .3)
    if a > 0:
        txt(od, (W / 2, 420), "यम दीपदान", 130, GOLD, a, sw=10)
        glow(o, W / 2, 900, 360, a)
        diya(od, W / 2, 1010, 2.2, t, a, flames=4)
        b = ease((t - at("s6", "दक्षिण")) / .3) * a
        ax, ay = W / 2, 1250
        od.polygon([(ax - 40, ay), (ax + 40, ay), (ax + 40, ay + 70), (ax + 80, ay + 70), (ax, ay + 150), (ax - 80, ay + 70), (ax - 40, ay + 70)], fill=(255, 150, 20, int(255 * b)))
        txt(od, (W / 2 + 230, ay + 80), "दक्षिण", 70, (255, 255, 255), b, sw=6)
        txt(od, (W / 2 - 250, ay + 80), "सरसों तेल", 60, CREAM, b, sw=6)
    # S7: CTA
    a = ease((t - S("s7")) / .3)
    if a > 0:
        glow(o, W / 2, 800, 330, a)
        coin(od, W / 2 - 40, 820, 2.2 + .1 * math.sin(t * 4), a)
        txt(od, (W / 2, 480), "आप क्या खरीद रहे हैं", 92, GOLD, a, sw=9)
        b = ease((t - at("s7", "कमेंट")) / .3)
        od.rounded_rectangle([W / 2 - 300, 1110, W / 2 + 300, 1240], radius=65, fill=(200, 30, 50, int(255 * b)))
        txt(od, (W / 2, 1175), "कमेंट में बताइए", 72, (255, 255, 255), b, sw=0)
        txt(od, (W / 2, 1360), "शुभ धनतेरस", 100, CREAM, b, sw=8)
    subtitle(od, t)
    img.alpha_composite(o)
    img = img.convert("RGB")
    lt = DUR - .6  # loop crossfade to first frame
    if t > lt:
        img = Image.blend(img, FIRST, ease((t - lt) / .6))
    return img

def build_audio(path):
    vo, sr = sf.read("/home/claude/dhanteras/vo.wav", dtype="float32"); n = len(vo); tt = np.arange(n) / sr
    drone = (np.sin(2 * np.pi * 130.8 * tt) * .5 + np.sin(2 * np.pi * 196 * tt) * .35 + np.sin(2 * np.pi * 261.6 * tt) * .2) * (1 + .3 * np.sin(2 * np.pi * .25 * tt))
    drone = drone.astype(np.float32) * .045
    bells = np.zeros(n, np.float32)
    for s in SEGS:
        st = int(max(0, s["start"] - .25) * sr); m = min(n - st, int(1.8 * sr)); x = np.arange(m) / sr
        b = (np.sin(2 * np.pi * 880 * x) + .5 * np.sin(2 * np.pi * 1320 * x) + .3 * np.sin(2 * np.pi * 2210 * x)) * np.exp(-x * 3.5)
        bells[st:st + m] += b.astype(np.float32) * .12
    out = vo + drone + bells
    out[:int(.3 * sr)] *= np.linspace(0, 1, int(.3 * sr)); out[-int(.6 * sr):] *= np.linspace(1, 0, int(.6 * sr))
    out = np.clip(out / max(1.0, np.max(np.abs(out)) / .97), -1, 1)
    sf.write(path, out, sr)

FIRST = None
if __name__ == "__main__":
    FIRST = frame(0)
    if len(sys.argv) > 1:
        secs = [float(x) for x in sys.argv[1].split(",")]
        ims = [frame(int(s * FPS)).resize((270, 480)) for s in secs]
        g = Image.new("RGB", (270 * len(ims), 480))
        for k, im in enumerate(ims): g.paste(im, (k * 270, 0))
        g.save("/home/claude/dhanteras/prev.jpg"); sys.exit()
    wav = "/home/claude/dhanteras/mix.wav"; build_audio(wav)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait(); print("done", DUR)
