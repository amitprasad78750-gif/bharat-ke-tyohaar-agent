import sys, json, math; sys.path.insert(0, "/home/claude")
import paperkit as K
from paperkit import *
SEGS = json.load(open("/home/claude/somvar/vo.json"))["segs"]; SEG = {s["id"]: s for s in SEGS}
S = lambda i: SEG[i]["start"]
def at(i, word):
    s = SEG[i]; p = s["text"].find(word) / max(1, len(s["text"])); return s["start"] + (s["end"] - s["start"]) * p - .25
BG = P.bg_base((205, 225, 245), (150, 175, 220)); P.hills(BG, 1380, (110, 130, 180), 21, 25)
BG2 = P.bg_base((250, 228, 185), (235, 190, 130)); P.hills(BG2, 1400, (200, 150, 100), 22, 25)
def scene(t):
    if t < S("n2"):
        img = BG.copy(); glowc(img, W / 2, 900, 360, 1, (255, 255, 220))
        label(img, "सोमवार को", W / 2, 300, t, (40, 60, 140), (255, 245, 220), 96, 1)
        label(img, "बेलपत्र मत तोड़ना", W / 2, 450, t, (200, 30, 50), (255, 245, 220), 96, 2)
        place(img, "bel_x", lambda: sp_cross_overlay(sp_belpatra()), W / 2, 920, t, 1.25, 2)
        q = ease((t - at("n1", "एक")) / .25)
        label(img, "एक दिन पहले तोड़ें", W / 2, 1330, t, (40, 130, 70), (255, 255, 255), 74, 3, a=q, rot=-2)
    elif t < S("n3"):
        img = BG2.copy(); glowc(img, W / 2, 1000, 380, 1)
        label(img, "शिव पूजा", W / 2, 290, t, (40, 60, 140), (255, 245, 220), 90, 4)
        place(img, "shivling", sp_shivling, W / 2 + 60, 1050, t, 1.3, .8)
        tj = at("n2", "जल")
        if t > tj:
            q = ease((t - tj) / .25)
            place(img, "lota_t", sp_lota_tilt, W / 2 - 170, 620, t, .7, 1.5, a=q)
            d = ImageDraw.Draw(img)
            for k in range(8):
                yy = 700 + ((t * 600 + k * 60) % 330)
                d.ellipse([W / 2 - 20, yy, W / 2, yy + 34], fill=(110, 170, 230, int(230 * q)))
            label(img, "जल अभिषेक", 300, 470, t, (60, 120, 200), (255, 255, 255), 64, 5, a=q, rot=-3)
        tb = at("n2", "तीन")
        if t > tb:
            q = ease((t - tb) / .3)
            place(img, "bel", sp_belpatra, W / 2 + 10, 820 + 60 * q, t, .8, 2, a=q)
            label(img, "३ पत्ती  साबुत", 820, 470, t, (40, 130, 70), (255, 255, 255), 60, 6, a=q, rot=3)
        tc = at("n2", "चिकनी")
        if t > tc: label(img, "चिकनी तरफ़ नीचे", W / 2, 1450, t, size=64, seed=7, a=ease((t - tc) / .25))
    elif t < S("n4"):
        img = BG2.copy()
        label(img, "व्रत के नियम", W / 2, 290, t, (40, 60, 140), (255, 245, 220), 90, 8)
        tick_card(img, "phal", sp_phalahar, "एक बार फलाहार", 300, 720, t, at("n3", "एक"), .6, w=440, seed=9)
        tick_card(img, "satvik", lambda: item("bhaat"), "सात्विक भोजन", 780, 720, t, at("n3", "सात्विक"), .6, w=440, seed=10)
        x_card(img, "og", sp_onion_garlic, "प्याज़ लहसुन नहीं", 300, 1180, t, at("n3", "प्याज़"), .6, w=440, seed=11)
        x_card(img, "slp", sp_sleep, "दिन में सोना नहीं", 780, 1180, t, at("n3", "सोना"), .6, w=440, seed=12)
    else:
        img = BG.copy(); glowc(img, W / 2, 950, 420, 1, (255, 240, 180))
        place(img, "trishul", sp_trishul, 230, 950, t, 1.0, 1.5)
        place(img, "shivling", sp_shivling, W / 2 + 80, 1050, t, 1.3, .8)
        place(img, "bel2", sp_belpatra, W / 2 + 20, 880, t, .7, 1)
        label(img, "कमेंट करें", W / 2, 320, t, (40, 60, 140), (255, 245, 220), 84, 13)
        label(img, "हर हर महादेव", W / 2, 1420, t, (200, 30, 50), (255, 245, 220), 96, 14)
    return img
ticks = [at("n2", "जल"), at("n2", "तीन"), at("n3", "एक"), at("n3", "सात्विक"), at("n3", "प्याज़"), at("n3", "सोना")]
render(SEGS, scene, "/home/claude/somvar_vrat_niyam_paper.mp4", "/home/claude/somvar/", "मान्यताओं पर आधारित", ticks, "/home/claude/somvar/vo.wav")
