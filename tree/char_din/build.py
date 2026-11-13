"""Chhath ke 4 din — paper cut-out checklist (12 fps)."""
import math, subprocess, sys, json, random, importlib.util
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "/home/claude/tts")
import raju_shyam as R
def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
P = _load("paper", "/home/claude/paper/build.py")

W, H, FPS = 1080, 1920, 12
P.FPS = FPS
VJ = json.load(open("/home/claude/char_din/vo.json")); SEGS = VJ["segs"]; SEG = {s["id"]: s for s in SEGS}
DUR = SEGS[-1]["end"] + 1.0
OUT = "/home/claude/chhath_char_din_paper.mp4"
dfont, ease, clamp = R.dfont, R.ease, R.clamp
S = lambda i: SEG[i]["start"]; E = lambda i: SEG[i]["end"]
INK, GOLD = P.INK, P.GOLD
place, label, glowc, cutout, strip, prop, doll = P.place, P.label, P.glowc, P.cutout, P.strip, P.prop, P.doll
def at(i, word):
    s = SEG[i]; p = s["text"].find(word) / max(1, len(s["text"])); return s["start"] + (s["end"] - s["start"]) * p - .25

def new_sp(w=520, h=520):
    sp = Image.new("RGBA", (w, h), (0, 0, 0, 0)); return sp, ImageDraw.Draw(sp)

def item(kind):
    sp, d = new_sp(); c = 260
    if kind == "lota":
        d.ellipse([c - 150, 200, c + 150, 440], fill=(215, 160, 50)); d.polygon([(c - 70, 210), (c + 70, 210), (c + 95, 110), (c - 95, 110)], fill=(225, 175, 60))
        d.ellipse([c - 105, 85, c + 105, 135], fill=(120, 180, 230)); d.ellipse([c - 80, 260, c - 20, 330], fill=(250, 220, 130))
        for k in range(3): d.arc([c - 60 + k * 40, 20 + k * 8, c - 20 + k * 40, 90], 200, 340, fill=(120, 180, 230), width=10)
    elif kind == "kaddu":  # Bihar 'kaddu' = lauki (bottle gourd)
        d.ellipse([c - 120, 230, c + 120, 470], fill=(150, 200, 90)); d.ellipse([c - 70, 60, c + 70, 300], fill=(150, 200, 90))
        d.rectangle([c - 12, 30, c + 12, 75], fill=(90, 120, 50))
        for k in range(4): d.ellipse([c - 60 + k * 30, 300 + (k % 2) * 40, c - 50 + k * 30, 310 + (k % 2) * 40], fill=(200, 230, 150))
    elif kind in ("dal", "bhaat", "kheer"):
        d.chord([c - 190, 170, c + 190, 450], 0, 180, fill=(195, 195, 205)); d.rectangle([c - 190, 300, c + 190, 312], fill=(160, 160, 170))
        col = {"dal": (240, 190, 40), "bhaat": (250, 250, 245), "kheer": (205, 150, 90)}[kind]
        d.ellipse([c - 185, 250, c + 185, 340], fill=col)
        rr = random.Random(3)
        for _ in range(24 if kind == "bhaat" else 14):
            x, y = c + rr.uniform(-150, 150), 295 + rr.uniform(-28, 28)
            if kind == "bhaat": d.ellipse([x - 10, y - 4, x + 10, y + 4], fill=(225, 225, 215))
            elif kind == "dal": d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(220, 160, 30))
            else: d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(150, 95, 50))
    elif kind == "roti":
        for k, (dx, dy) in enumerate(((-40, 30), (30, 0))):
            d.ellipse([c - 170 + dx, 140 + dy, c + 170 + dx, 400 + dy], fill=(230, 190, 120), outline=(190, 140, 80), width=6)
            rr = random.Random(k)
            for _ in range(10):
                x, y = c + dx + rr.uniform(-120, 120), 270 + dy + rr.uniform(-80, 80)
                d.ellipse([x - 12, y - 8, x + 12, y + 8], fill=(170, 110, 50))
    elif kind == "clock":
        d.ellipse([c - 200, 60, c + 200, 460], fill=(250, 245, 230), outline=(200, 40, 50), width=22)
        for k in range(12):
            an = k * math.pi / 6; d.line([(c + math.cos(an) * 150, 260 + math.sin(an) * 150), (c + math.cos(an) * 175, 260 + math.sin(an) * 175)], fill=INK, width=8)
        d.line([(c, 260), (c, 140)], fill=INK, width=14); d.line([(c, 260), (c + 90, 300)], fill=INK, width=12)
        d.ellipse([c - 16, 244, c + 16, 276], fill=(200, 40, 50))
    elif kind == "jal":   # no-water sign
        d.polygon([(c, 70), (c + 120, 280), (c + 120, 330), (c - 120, 330), (c - 120, 280)], fill=(120, 180, 230))
        d.ellipse([c - 120, 230, c + 120, 450], fill=(120, 180, 230))
        d.ellipse([c - 210, 50, c + 210, 470], outline=(210, 30, 40), width=34)
        d.line([(c - 150, 110), (c + 150, 410)], fill=(210, 30, 40), width=34)
    elif kind == "thekua":
        for k, (dx, dy) in enumerate(((-90, 40), (90, 40), (0, -60))):
            d.ellipse([c + dx - 110, 250 + dy - 80, c + dx + 110, 250 + dy + 80], fill=(190, 115, 40), outline=(140, 80, 25), width=6)
            for j in range(-3, 4): d.line([(c + dx + j * 26 - 14, 250 + dy - 50), (c + dx + j * 26 + 14, 250 + dy + 50)], fill=(150, 85, 25), width=6)
    return sp

def vrati(arms_up=True):
    sp, d = new_sp(520, 900); cx = 260; SK = P.SK
    d.polygon([(cx - 110, 380), (cx + 110, 380), (cx + 180, 860), (cx - 180, 860)], fill=(250, 200, 30))
    d.polygon([(cx + 110, 380), (cx + 40, 380), (cx - 150, 860), (cx - 60, 860)], fill=(220, 40, 50))
    if arms_up:
        for k in (-1, 1): d.rounded_rectangle([cx + k * 120 - 30, 160, cx + k * 120 + 30, 420], radius=28, fill=SK)
    d.rectangle([cx - 28, 330, cx + 28, 390], fill=SK)
    d.ellipse([cx - 150, 110, cx + 150, 380], fill=(40, 30, 25))
    d.ellipse([cx - 100, 125, cx + 100, 350], fill=SK)
    d.pieslice([cx - 104, 115, cx + 104, 270], 180, 360, fill=(40, 30, 25))
    d.line([(cx, 115), (cx, 175)], fill=(250, 140, 20), width=14)   # orange (peela) sindoor from nose to hairline
    P.face(d, cx, 250, 95, "smile", "closed")
    return sp

BG_HOME = P.bg_base((255, 228, 180), (245, 200, 140)); P.hills(BG_HOME, 1380, (205, 150, 95), 8, 25)
BG_EVE = P.bg_base((250, 160, 110), (150, 80, 110)); P.hills(BG_EVE, 1350, (110, 60, 80), 9, 30)
def ghaat_bg(sunrise):
    top, bot = ((255, 200, 140), (250, 170, 120)) if sunrise else ((250, 150, 70), (180, 70, 70))
    img = P.bg_base(top, bot); P.hills(img, 1000, (110, 70, 70) if not sunrise else (140, 110, 90), 11, 35)
    rv = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(rv)
    d.rectangle([0, 1080, W, H], fill=(60, 110, 160, 255) if sunrise else (50, 70, 120, 255))
    c, pad = cutout(rv, 0, (0, -8), 8); img.alpha_composite(c, (-pad, -pad))
    return img
BG_SET, BG_RISE = ghaat_bg(False), ghaat_bg(True)

def tick_card(img, key, fn, lab, x, y, t, t0, sc=.55, w=430, h=380, seed=0):
    if t < t0: return
    q = ease((t - t0) / .2)
    pop = 1 + .2 * math.sin(clamp((t - t0) / .3) * math.pi)
    def mk():
        sp = strip(w, h, (255, 250, 236), 200 + seed)
        return sp
    place(img, ("card", w, h, seed), mk, x, y, t, 1.0, .8, a=q, seed=seed)
    place(img, key, fn, x, y - 40, t, sc * pop, 1.2, a=q, seed=seed)
    dd = ImageDraw.Draw(img); dd.text((x, y + h / 2 - 50), lab, font=dfont(54), fill=INK + (255,), anchor="mm")
    if t > t0 + .35:  # green tick sticker
        k = ease((t - t0 - .35) / .15)
        cx, cy = x + w / 2 - 30, y - h / 2 + 30
        dd.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(40, 140, 70, int(255 * k)), outline=(255, 255, 255, int(255 * k)), width=6)
        dd.line([(cx - 15, cy), (cx - 3, cy + 13), (cx + 17, cy - 13)], fill=(255, 255, 255, int(255 * k)), width=8)

def day_badge(img, num, date, name, t, t0, col):
    q = ease((t - t0) / .25)
    def mk():
        sp, d = new_sp(300, 300); d.ellipse([10, 10, 290, 290], fill=col); d.ellipse([30, 30, 270, 270], outline=(255, 245, 220), width=8)
        d.text((150, 120), "दिन", font=dfont(56), fill=(255, 245, 220), anchor="mm"); d.text((150, 200), num, font=dfont(110), fill=(255, 245, 220), anchor="mm")
        return sp
    place(img, ("badge", num), mk, 180, 330, t, .85, 2, a=q, seed=1)
    label(img, name, 640, 290, t, col, (255, 245, 220), 82, 300 + int(col[0]), a=q, rot=-2)
    label(img, date, 640, 420, t, size=58, seed=400 + int(col[1]), a=q, rot=2)

def frame(i):
    t = i / FPS
    if t < S("n2"):   # HOOK — 4 paper day cards fanned
        img = BG_SET.copy()
        glowc(img, W / 2, 950, 380, 1)
        place(img, "sun", lambda: prop("sun"), W / 2, 980, t, 1.1, 3, rot=t * 20)
        cols = [(40, 60, 140), (40, 130, 70), (230, 110, 20), (200, 30, 50)]
        for k, (num, col) in enumerate(zip("१२३४", cols)):
            t0 = .15 + k * .35
            def mk(num=num, col=col):
                sp, d = new_sp(240, 320); d.rounded_rectangle([10, 10, 230, 310], radius=30, fill=col)
                d.text((120, 110), "दिन", font=dfont(54), fill=(255, 245, 220), anchor="mm"); d.text((120, 210), num, font=dfont(120), fill=(255, 245, 220), anchor="mm")
                return sp
            x = 180 + k * 240; y = 1370 - (25 if k in (1, 2) else 0)
            if t > t0: place(img, ("hk", k), mk, x, y, t, 1.0, 2, a=ease((t - t0) / .2), seed=k, rot=(-8, -3, 3, 8)[k])
        label(img, "छठ के ४ दिन", W / 2, 300, t, (200, 30, 50), (255, 245, 220), 110, 1)
        label(img, "किस दिन क्या करें", W / 2, 470, t, size=80, seed=2)
        q = ease((t - at("n1", "ग़लती")) / .25)
        label(img, "ग़लती मत करना", W / 2, 640, t, (40, 40, 60), (255, 220, 120), 64, 3, a=q, rot=-3)
    elif t < S("n3"):  # Day 1
        img = BG_HOME.copy()
        day_badge(img, "१", "१३ नवंबर  शुक्रवार", "नहाय खाय", t, S("n2"), (40, 60, 140))
        tick_card(img, "lota", lambda: item("lota"), "स्नान", 300, 760, t, at("n2", "स्नान"), seed=1)
        tick_card(img, "kaddu", lambda: item("kaddu"), "कद्दू की सब्ज़ी", 780, 760, t, at("n2", "कद्दू"), seed=2)
        tick_card(img, "dal", lambda: item("dal"), "चने की दाल", 300, 1200, t, at("n2", "चने"), seed=3)
        tick_card(img, "bhaat", lambda: item("bhaat"), "चावल", 780, 1200, t, at("n2", "चावल"), seed=4)
    elif t < S("n4"):  # Day 2 Kharna
        img = BG_EVE.copy()
        day_badge(img, "२", "१४ नवंबर  शनिवार", "खरना", t, S("n3"), (40, 130, 70))
        tick_card(img, "kheer", lambda: item("kheer"), "गुड़ की खीर", 300, 760, t, at("n3", "गुड़"), seed=5)
        tick_card(img, "roti", lambda: item("roti"), "रोटी", 780, 760, t, at("n3", "रोटी"), seed=6)
        t36 = at("n3", "छत्तीस")
        if t > t36:
            q = ease((t - t36) / .25)
            place(img, "clock", lambda: item("clock"), 300, 1230, t, .65, 2, a=q)
            place(img, "jal", lambda: item("jal"), 780, 1230, t, .6, 2, a=q)
            label(img, "३६ घंटे", 300, 1480, t, (200, 30, 50), (255, 245, 220), 70, 7, a=q)
            label(img, "निर्जला व्रत", 780, 1480, t, (200, 30, 50), (255, 245, 220), 64, 8, a=q)
    elif t < S("n5"):  # Day 3 sandhya arghya
        img = BG_SET.copy()
        sy = 820 + 160 * ease((t - S("n4")) / (S("n5") - S("n4")))
        glowc(img, W / 2, sy, 300, 1)
        place(img, "sun", lambda: prop("sun"), W / 2, sy, t, .9, 2, rot=t * 15)
        day_badge(img, "३", "१५ नवंबर  रविवार", "संध्या अर्घ्य", t, S("n4"), (230, 110, 20))
        place(img, "daura", lambda: daura(), 220, 1200, t, .7, a=ease((t - at("n4", "दउरा")) / .25))
        place(img, "vrati", lambda: vrati(), 640, 1230, t, .8, 1.2)
        place(img, "soop", lambda: prop("soop"), 640, 905, t, .7, 1.2)
        q = ease((t - at("n4", "डूबते")) / .25)
        label(img, "डूबते सूरज को अर्घ्य", W / 2, 1560, t, (40, 40, 80), (255, 220, 120), 68, 9, a=q)
    elif t < S("n6"):  # Day 4 usha arghya + parana
        img = BG_RISE.copy()
        sy = 1000 - 220 * ease((t - S("n5")) / 3)
        glowc(img, W / 2, sy, 320, 1)
        place(img, "sun", lambda: prop("sun"), W / 2, sy, t, .9, 2, rot=t * 15)
        day_badge(img, "४", "१६ नवंबर  सोमवार", "उषा अर्घ्य", t, S("n5"), (200, 30, 50))
        place(img, "vrati", lambda: vrati(), 400, 1230, t, .8, 1.2)
        place(img, "soop", lambda: prop("soop"), 400, 905, t, .7, 1.2)
        tp = at("n5", "पारण")
        if t > tp:
            q = ease((t - tp) / .25)
            place(img, "thekua", lambda: item("thekua"), 820, 1200, t, .55, 2, a=q)
            label(img, "पारण", 820, 1360, t, (40, 130, 70), (255, 255, 255), 72, 10, a=q)
        q = ease((t - at("n5", "उगते")) / .25)
        label(img, "उगते सूरज को अर्घ्य", W / 2, 1560, t, (40, 40, 80), (255, 220, 120), 68, 11, a=q)
    else:  # CTA
        img = BG_RISE.copy()
        glowc(img, W / 2, 700, 380, 1)
        place(img, "sun", lambda: prop("sun"), W / 2, 700, t, 1.0, 2, rot=t * 15)
        label(img, "सेव करें", W / 2, 320, t, (40, 60, 140), (255, 245, 220), 100, 12)
        place(img, "soop", lambda: prop("soop"), W / 2, 1130, t, 1.0, 1.5)
        q = ease((t - at("n6", "कमेंट")) / .25)
        label(img, "कमेंट करें  जय छठी मैया", W / 2, 1450, t, (200, 30, 50), (255, 245, 220), 72, 13, a=q)
    # subtitle strip
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
    if t > S("n2"): dd.text((W / 2, 118), "परंपरा पर आधारित  हर घर की रीत अलग हो सकती है", font=dfont(30), fill=(255, 250, 235, 230), anchor="mm", stroke_width=3, stroke_fill=(90, 40, 20, 200))
    return img.convert("RGB")

def daura():
    sp, d = new_sp(); c = 260
    d.polygon([(c - 220, 200), (c + 220, 200), (c + 170, 440), (c - 170, 440)], fill=(210, 165, 85))
    for k in range(5): d.line([(c - 210 + k * 8, 230 + k * 45), (c + 210 - k * 8, 230 + k * 45)], fill=(160, 120, 50), width=8)
    d.ellipse([c - 225, 170, c + 225, 230], fill=(190, 145, 70))
    d.ellipse([c - 160, 120, c - 40, 220], fill=(120, 75, 35)); d.arc([c - 30, 80, c + 140, 230], 200, 320, fill=(250, 210, 40), width=34)
    d.ellipse([c + 100, 140, c + 190, 220], fill=(240, 120, 30))
    return sp

def build_audio(path):
    vo, sr = sf.read("/home/claude/char_din/vo.wav", dtype="float32"); n = int(DUR * sr); vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]; tt = np.arange(n) / sr
    bed_ = sum(np.sin(2 * np.pi * f * tt + ph) * g for f, g, ph in ((146.8, .5, 0), (220.0, .3, 1), (293.7, .2, 2))) * (1 + .25 * np.sin(2 * np.pi * .4 * tt))
    talk = np.zeros(n, np.float32)
    for s in SEGS: talk[int(s["start"] * sr):int(s["end"] * sr)] = 1
    talk = np.convolve(talk, np.ones(int(.2 * sr)) / int(.2 * sr), mode="same")
    out = vo + (bed_ * .035 * (1 - .7 * np.clip(talk, 0, 1))).astype(np.float32)
    def add(t0, sig):
        st = int(max(0, t0) * sr); m = min(n - st, len(sig))
        if m > 0: out[st:st + m] += sig[:m]
    def bell(f=700, v=.06, L=1.4, dec=3):
        x = np.arange(int(L * sr)) / sr
        return ((np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 2.76 * x)) * np.exp(-x * dec) * v).astype(np.float32)
    def rustle(v=.05):
        x = np.arange(int(.35 * sr)) / sr; nz = np.random.RandomState(3).randn(len(x)).astype(np.float32)
        nz = np.convolve(nz, np.ones(6) / 6, mode="same") - np.convolve(nz, np.ones(60) / 60, mode="same")
        return (nz * np.sin(np.pi * x / x[-1]) * v).astype(np.float32)
    add(0, bell())
    for k in range(4): add(.15 + k * .35, rustle(.04))
    for s in SEGS[1:]: add(s["start"] - .3, rustle()); add(s["start"] - .2, bell(700, .045))
    for sid, words in (("n2", ["स्नान", "कद्दू", "चने", "चावल"]), ("n3", ["गुड़", "रोटी", "छत्तीस"]), ("n4", ["दउरा", "डूबते"]), ("n5", ["उगते", "पारण"])):
        for w in words: add(at(sid, w) + .35, bell(1320, .035, .3, 18))
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
        g.save("/home/claude/char_din/prev.jpg"); sys.exit()
    wav = "/home/claude/char_din/mix.wav"; build_audio(wav)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", OUT], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait(); print("done", DUR)
