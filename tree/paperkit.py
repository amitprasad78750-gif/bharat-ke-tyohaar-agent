"""Shared paper cut-out kit: sprites + render/audio loop for short checklist videos."""
import math, subprocess, sys, json, random, importlib.util
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tts")
import raju_shyam as R
def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
P = _load("paper", "/home/claude/paper/build.py")
CD = _load("chardin", "/home/claude/char_din/build.py")
W, H, FPS = 1080, 1920, 12
dfont, ease, clamp = R.dfont, R.ease, R.clamp
INK, GOLD, SK = P.INK, P.GOLD, P.SK
place, label, glowc, cutout, strip, prop, item, tick_card = P.place, P.label, P.glowc, P.cutout, P.strip, P.prop, CD.item, CD.tick_card

def new_sp(w=520, h=520):
    sp = Image.new("RGBA", (w, h), (0, 0, 0, 0)); return sp, ImageDraw.Draw(sp)

def leaf(d, cx, cy, L, Wd, ang, col, vein=(150, 200, 110)):
    pts = []
    for k in range(21):
        u = k / 20; r = math.sin(u * math.pi) * Wd
        pts.append((u * L, r))
    pts += [(u * L, -math.sin(u * math.pi) * Wd) for u in [k / 20 for k in range(20, -1, -1)]]
    ca, sa = math.cos(ang), math.sin(ang)
    P2 = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]
    d.polygon(P2, fill=col)
    d.line([(cx, cy), (cx + L * ca, cy + L * sa)], fill=vein, width=5)

def sp_belpatra():
    sp, d = new_sp()
    d.line([(260, 470), (260, 300)], fill=(90, 120, 50), width=12)
    for ang in (-math.pi / 2, -math.pi / 2 - 1.0, -math.pi / 2 + 1.0):
        leaf(d, 260, 300, 230 if ang == -math.pi / 2 else 180, 62, ang, (60, 140, 50))
    return sp

def sp_shivling():
    sp, d = new_sp(560, 560); c = 280
    d.polygon([(c - 250, 400), (c + 150, 400), (c + 250, 360), (c + 260, 420), (c + 150, 470), (c - 250, 470)], fill=(110, 110, 120))   # yoni with spout
    d.ellipse([c - 250, 360, c + 150, 440], fill=(130, 130, 140))
    d.rectangle([c - 110, 170, c + 10, 400], fill=(80, 80, 90)); d.ellipse([c - 110, 110, c + 10, 230], fill=(80, 80, 90))
    for k in range(3): d.line([(c - 95, 230 + k * 18), (c - 5, 230 + k * 18)], fill=(245, 245, 245), width=7)
    d.ellipse([c - 60, 252, c - 40, 272], fill=(220, 30, 30))
    return sp

def sp_lota_tilt():
    sp, d = new_sp(); c = 260
    img, dd = new_sp()
    dd.ellipse([c - 150, 200, c + 150, 440], fill=(215, 160, 50)); dd.polygon([(c - 70, 210), (c + 70, 210), (c + 95, 110), (c - 95, 110)], fill=(225, 175, 60))
    dd.ellipse([c - 105, 85, c + 105, 135], fill=(120, 180, 230)); dd.ellipse([c - 80, 260, c - 20, 330], fill=(250, 220, 130))
    return img.rotate(-55, resample=Image.BICUBIC, center=(c, 260))

def sp_cross_overlay(base):
    sp = base.copy(); d = ImageDraw.Draw(sp); w, h = sp.size
    d.ellipse([20, 20, w - 20, h - 20], outline=(210, 30, 40), width=30)
    d.line([(w * .2, h * .2), (w * .8, h * .8)], fill=(210, 30, 40), width=30)
    return sp

def sp_onion_garlic():
    sp, d = new_sp(); c = 260
    d.ellipse([c - 200, 200, c - 20, 400], fill=(170, 60, 110)); d.polygon([(c - 130, 210), (c - 90, 210), (c - 110, 120)], fill=(170, 60, 110))
    for k in range(3): d.arc([c - 190 + k * 30, 210, c - 70 + k * 30, 390], 250, 290, fill=(200, 110, 150), width=5)
    d.ellipse([c + 10, 220, c + 200, 410], fill=(245, 240, 230)); d.polygon([(c + 85, 230), (c + 125, 230), (c + 105, 150)], fill=(245, 240, 230))
    for k in range(4): d.line([(c + 40 + k * 40, 240), (c + 40 + k * 40, 400)], fill=(215, 205, 190), width=5)
    return sp_cross_overlay(sp)

def sp_sleep():
    sp, d = new_sp(); c = 260
    d.rounded_rectangle([c - 200, 300, c + 200, 360], radius=20, fill=(150, 100, 70))
    d.ellipse([c - 210, 250, c - 110, 330], fill=(250, 250, 245))
    d.rounded_rectangle([c - 130, 270, c + 200, 330], radius=30, fill=(90, 130, 200))
    d.ellipse([c - 180, 220, c - 90, 300], fill=SK)
    for k, (x, y, s) in enumerate(((c, 200, 50), (c + 60, 140, 64), (c + 130, 70, 78))):
        d.text((x, y), "z", font=R.lfont(s) if hasattr(R, "lfont") else dfont(s), fill=(60, 60, 120), anchor="mm")
    return sp_cross_overlay(sp)

def sp_phalahar():
    sp, d = new_sp(); c = 260
    d.ellipse([c - 220, 300, c + 220, 420], fill=(200, 200, 210)); d.ellipse([c - 200, 290, c + 200, 390], fill=(230, 230, 236))
    d.ellipse([c - 160, 210, c - 40, 330], fill=(220, 40, 50)); d.ellipse([c - 115, 195, c - 95, 215], fill=(80, 120, 40))
    d.arc([c - 40, 150, c + 130, 330], 200, 320, fill=(250, 210, 40), width=36)
    d.ellipse([c + 60, 230, c + 170, 330], fill=(240, 120, 30))
    for k in range(10): d.ellipse([c - 60 + (k % 5) * 25, 320 + (k // 5) * 18, c - 44 + (k % 5) * 25, 334 + (k // 5) * 18], fill=(250, 250, 240))
    return sp

def sp_trishul():
    sp, d = new_sp(300, 700); c = 150; col = (90, 90, 100)
    d.line([(c, 690), (c, 220)], fill=col, width=18); d.line([(c - 90, 220), (c + 90, 220)], fill=col, width=18)
    for k in (-1, 0, 1):
        d.polygon([(c + k * 90 - 16, 220), (c + k * 90 + 16, 220), (c + k * 90, 220 - (170 if k == 0 else 130))], fill=col)
    d.ellipse([c - 45, 300, c + 45, 380], fill=(200, 150, 90)); d.polygon([(c - 45, 300), (c + 45, 300), (c, 340)], fill=(160, 100, 50))
    d.polygon([(c - 45, 380), (c + 45, 380), (c, 340)], fill=(160, 100, 50))
    return sp

def sp_vishnu(eyes="open"):
    sp, d = new_sp(560, 920); cx = 280; BL = (70, 120, 200)
    d.ellipse([cx - 230, 20, cx + 230, 470], fill=(255, 220, 90)); d.ellipse([cx - 200, 50, cx + 200, 440], fill=(255, 240, 160))
    d.polygon([(cx - 130, 390), (cx + 130, 390), (cx + 190, 900), (cx - 190, 900)], fill=(250, 200, 30))   # pitambar
    d.polygon([(cx - 130, 390), (cx + 130, 390), (cx + 110, 560), (cx - 110, 560)], fill=BL)
    for k in range(9):
        an = math.pi * k / 8; d.ellipse([cx - 110 + 220 * k / 8 - 13, 400 + math.sin(an) * 120 - 13, cx - 110 + 220 * k / 8 + 13, 400 + math.sin(an) * 120 + 13], fill=((250, 150, 30) if k % 2 else (255, 230, 80)))
    for k in (-1, 1):
        d.rounded_rectangle([cx + k * 165 - 32, 300, cx + k * 165 + 32, 520], radius=30, fill=BL)
        d.ellipse([cx + k * 165 - 40, 250, cx + k * 165 + 40, 330], fill=BL)
    # chakra (right) and shankh (left)
    rx, ry = cx + 190, 220
    d.ellipse([rx - 55, ry - 55, rx + 55, ry + 55], outline=(240, 170, 30), width=12)
    for k in range(8): an = k * math.pi / 4; d.line([(rx, ry), (rx + math.cos(an) * 50, ry + math.sin(an) * 50)], fill=(240, 170, 30), width=6)
    lx, ly = cx - 190, 220
    d.polygon([(lx - 45, ly + 40), (lx + 40, ly - 50), (lx + 55, ly + 10), (lx + 10, ly + 55)], fill=(250, 248, 240), outline=(200, 180, 150))
    d.rectangle([cx - 30, 340, cx + 30, 400], fill=BL)
    d.ellipse([cx - 105, 130, cx + 105, 350], fill=BL)
    d.pieslice([cx - 108, 120, cx + 108, 270], 180, 360, fill=(30, 25, 40))
    d.polygon([(cx - 95, 160), (cx + 95, 160), (cx + 70, 40), (cx + 30, 80), (cx, 0), (cx - 30, 80), (cx - 70, 40)], fill=GOLD, outline=(180, 110, 0))
    d.ellipse([cx - 14, 95, cx + 14, 123], fill=(220, 30, 40))
    d.polygon([(cx - 14, 175), (cx + 14, 175), (cx, 230)], fill=(250, 240, 230)); d.line([(cx, 180), (cx, 225)], fill=(220, 30, 30), width=5)
    P.face(d, cx, 255, 95, "smile", eyes)
    return sp

def sp_flowers():
    sp, d = new_sp(); rr = random.Random(5)
    for k in range(7):
        x, y = 140 + (k % 4) * 80 + rr.uniform(-10, 10), 200 + (k // 4) * 110 + rr.uniform(-10, 10)
        for j in range(12):
            an = j * math.pi / 6; d.ellipse([x + math.cos(an) * 30 - 22, y + math.sin(an) * 30 - 22, x + math.cos(an) * 30 + 22, y + math.sin(an) * 30 + 22], fill=(250, 200 if k % 2 else 170, 20))
        d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=(230, 120, 10))
    return sp

def sp_tulsi():
    sp, d = new_sp(); c = 260
    d.polygon([(c - 120, 330), (c + 120, 330), (c + 90, 470), (c - 90, 470)], fill=(200, 100, 60))
    d.rectangle([c - 130, 310, c + 130, 340], fill=(220, 120, 70))
    d.line([(c, 330), (c, 100)], fill=(90, 70, 40), width=10)
    for k in range(7):
        y = 300 - k * 30
        for s in (-1, 1): leaf(d, c, y, 80 - k * 6, 26, (-.5 if s < 0 else -2.64) + 0 * k, (60, 150, 60))
    return sp

def sp_om():
    sp, d = new_sp(); d.ellipse([40, 40, 480, 480], fill=(250, 140, 30)); d.ellipse([70, 70, 450, 450], fill=(255, 210, 90))
    d.text((260, 270), "ॐ", font=dfont(300), fill=(170, 40, 30), anchor="mm"); return sp

def sp_book():
    sp, d = new_sp(); c = 260
    d.polygon([(c, 160), (c - 230, 120), (c - 230, 400), (c, 440)], fill=(250, 240, 210), outline=(200, 40, 50))
    d.polygon([(c, 160), (c + 230, 120), (c + 230, 400), (c, 440)], fill=(250, 240, 210), outline=(200, 40, 50))
    for k in range(6):
        d.line([(c - 200, 170 + k * 40), (c - 30, 200 + k * 40)], fill=(170, 120, 90), width=6)
        d.line([(c + 30, 200 + k * 40), (c + 200, 170 + k * 40)], fill=(170, 120, 90), width=6)
    d.rectangle([c - 240, 400, c + 240, 430], fill=(200, 40, 50)); return sp

def sp_deeprow():
    sp, _ = new_sp(560, 300)
    for k in range(4): P.D.diya(ImageDraw.Draw(sp), 70 + k * 140, 190, 1.0, 0, 1)
    return sp

def x_card(img, key, fn, lab, x, y, t, t0, sc=.55, w=430, h=380, seed=0):
    """'don't' card: same as tick card but with red cross sticker"""
    if t < t0: return
    q = ease((t - t0) / .2); pop = 1 + .2 * math.sin(clamp((t - t0) / .3) * math.pi)
    place(img, ("card", w, h, seed), lambda: strip(w, h, (255, 236, 230), 200 + seed), x, y, t, 1.0, .8, a=q, seed=seed)
    place(img, key, fn, x, y - 40, t, sc * pop, 1.2, a=q, seed=seed)
    ImageDraw.Draw(img).text((x, y + h / 2 - 50), lab, font=dfont(52), fill=(170, 20, 30, 255), anchor="mm")

def render(SEGS, scene, out, prefix, disclaimer, ticks, vo_path):
    SEG = {s["id"]: s for s in SEGS}; DUR = SEGS[-1]["end"] + .8
    def frame(i):
        t = i / FPS
        img = scene(t)
        dd = ImageDraw.Draw(img)
        for s in SEGS:
            if s["start"] - .05 <= t <= s["end"] + .2:
                words = R.clean(s["text"]).split(); f = dfont(52); lines, cur = [], []
                for w in words:
                    if dd.textlength(" ".join(cur + [w]), font=f) > W - 180 and cur: lines.append(cur); cur = [w]
                    else: cur.append(w)
                lines.append(cur)
                hh = 68 * len(lines) + 40; y0 = 1795 - hh / 2
                key = ("sub", len(lines))
                if key not in P.CACHE: P.CACHE[key] = cutout(strip(W - 120, int(hh), (255, 250, 235), 99 + len(lines)), 0, (6, 8), 5)
                c, pad = P.CACHE[key]
                img.alpha_composite(c, (int(40 - pad), int(y0 - 20 - pad)))
                y = 1795 - (len(lines) - 1) * 34
                for ln in lines: dd.text((W / 2, y), " ".join(ln), font=f, fill=INK + (255,), anchor="mm"); y += 68
        dd.text((W / 2, 70), "भारत के त्योहार", font=dfont(38), fill=(255, 250, 235, 230), anchor="mm", stroke_width=4, stroke_fill=(90, 40, 20, 200))
        if t > SEGS[1]["start"]: dd.text((W / 2, 118), disclaimer, font=dfont(30), fill=(255, 250, 235, 230), anchor="mm", stroke_width=3, stroke_fill=(90, 40, 20, 200))
        return img.convert("RGB")
    if len(sys.argv) > 1:
        secs = [float(x) for x in sys.argv[1].split(",")]
        ims = [frame(int(s * FPS)).resize((360, 640)) for s in secs]
        g = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): g.paste(im, (k * 360, 0))
        g.save(prefix + "prev.jpg"); return
    # audio
    vo, sr = sf.read(vo_path, dtype="float32"); n = int(DUR * sr); vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]; tt = np.arange(n) / sr
    bed_ = sum(np.sin(2 * np.pi * f * tt + ph) * g for f, g, ph in ((146.8, .5, 0), (220.0, .3, 1), (293.7, .2, 2))) * (1 + .25 * np.sin(2 * np.pi * .4 * tt))
    talk = np.zeros(n, np.float32)
    for s in SEGS: talk[int(s["start"] * sr):int(s["end"] * sr)] = 1
    talk = np.convolve(talk, np.ones(int(.2 * sr)) / int(.2 * sr), mode="same")
    outa = vo + (bed_ * .035 * (1 - .7 * np.clip(talk, 0, 1))).astype(np.float32)
    def add(t0, sig):
        st = int(max(0, t0) * sr); m = min(n - st, len(sig))
        if m > 0: outa[st:st + m] += sig[:m]
    def bell(f=700, v=.06, L=1.4, dec=3):
        x = np.arange(int(L * sr)) / sr
        return ((np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 2.76 * x)) * np.exp(-x * dec) * v).astype(np.float32)
    def rustle(v=.05):
        x = np.arange(int(.35 * sr)) / sr; nz = np.random.RandomState(3).randn(len(x)).astype(np.float32)
        nz = np.convolve(nz, np.ones(6) / 6, mode="same") - np.convolve(nz, np.ones(60) / 60, mode="same")
        return (nz * np.sin(np.pi * x / x[-1]) * v).astype(np.float32)
    add(0, bell())
    for s in SEGS[1:]: add(s["start"] - .3, rustle()); add(s["start"] - .2, bell(700, .045))
    for tk in ticks: add(tk + .35, bell(1320, .035, .3, 18))
    outa[-int(.5 * sr):] *= np.linspace(1, 0, int(.5 * sr))
    outa = np.clip(outa / max(1.0, np.max(np.abs(outa)) / .95), -1, 1)
    raw = prefix + "mix_raw.wav"; wav = prefix + "mix.wav"; sf.write(raw, outa, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    "highpass=f=80,equalizer=f=250:width_type=o:width=1:g=-2,equalizer=f=3200:width_type=o:width=1.2:g=4,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000", wav], check=True)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait(); print("done", DUR)
