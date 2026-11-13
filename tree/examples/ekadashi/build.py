import sys, json, math; sys.path.insert(0, "/home/claude")
import paperkit as K
from paperkit import *
SEGS = json.load(open("/home/claude/ekadashi/vo.json"))["segs"]; SEG = {s["id"]: s for s in SEGS}
S = lambda i: SEG[i]["start"]
def at(i, word):
    s = SEG[i]; p = s["text"].find(word) / max(1, len(s["text"])); return s["start"] + (s["end"] - s["start"]) * p - .25
BG = P.bg_base((255, 230, 160), (245, 185, 90)); P.hills(BG, 1400, (210, 140, 60), 31, 25)
BGN = P.bg_base((40, 50, 110), (120, 90, 160)); P.hills(BGN, 1400, (40, 40, 80), 32, 25)
def scene(t):
    if t < S("n2"):
        img = BG.copy(); glowc(img, W / 2, 900, 430, 1)
        label(img, "२० नवंबर", W / 2, 280, t, (40, 60, 140), (255, 245, 220), 90, 1)
        label(img, "देवउठनी एकादशी", W / 2, 430, t, (200, 30, 50), (255, 245, 220), 96, 2)
        awake = t > at("n1", "जागते")
        place(img, "vishnu_o" if awake else "vishnu_c", (lambda: sp_vishnu("open")) if awake else (lambda: sp_vishnu("closed")), W / 2, 1050, t, .95, 1)
        if awake: label(img, "विष्णु जी जागे", W / 2, 1530, t, (40, 130, 70), (255, 255, 255), 72, 3, a=ease((t - at("n1", "जागते")) / .25))
    elif t < S("n3"):
        img = BG.copy()
        label(img, "पूजा में चढ़ाएँ", W / 2, 290, t, (40, 60, 140), (255, 245, 220), 90, 4)
        tick_card(img, "diya", lambda: CD.item("lota") if False else sp_deeprow(), "दीया", 300, 720, t, at("n2", "दीया"), .55, w=440, seed=5)
        tick_card(img, "flw", sp_flowers, "पीले फूल", 780, 720, t, at("n2", "पीले"), .6, w=440, seed=6)
        tick_card(img, "phal", sp_phalahar, "फल", 300, 1180, t, at("n2", "फल,"), .6, w=440, seed=7)
        tick_card(img, "tulsi", sp_tulsi, "तुलसी दल", 780, 1180, t, at("n2", "तुलसी"), .6, w=440, seed=8)
    elif t < S("n4"):
        img = BGN.copy()
        label(img, "दिन भर और शाम", W / 2, 290, t, (240, 170, 30), INK, 88, 9)
        tick_card(img, "om", sp_om, "विष्णु मंत्र", 300, 720, t, at("n3", "मंत्र"), .55, w=440, seed=10)
        tick_card(img, "book", sp_book, "व्रत कथा", 780, 720, t, at("n3", "कथा"), .6, w=440, seed=11)
        tick_card(img, "deep", sp_deeprow, "शाम को दीपदान", W / 2, 1180, t, at("n3", "दीपदान"), .8, w=600, seed=12)
    else:
        img = BG.copy(); glowc(img, W / 2, 950, 420, 1)
        place(img, "vishnu_o", lambda: sp_vishnu("open"), W / 2, 980, t, .8, 1)
        label(img, "एकादशी तिथि", W / 2, 270, t, (40, 60, 140), (255, 245, 220), 80, 13)
        label(img, "२० नवंबर सुबह ७ बजकर १५ मिनट से", W / 2, 400, t, size=56, seed=14)
        q = ease((t - at("n4", "कमेंट")) / .25)
        label(img, "कमेंट करें  जय श्री हरि", W / 2, 1520, t, (200, 30, 50), (255, 245, 220), 74, 15, a=q)
    return img
ticks = [at("n2", "दीया"), at("n2", "पीले"), at("n2", "फल,"), at("n2", "तुलसी"), at("n3", "मंत्र"), at("n3", "कथा"), at("n3", "दीपदान")]
render(SEGS, scene, "/home/claude/devuthani_ekadashi_paper.mp4", "/home/claude/ekadashi/", "मान्यताओं पर आधारित  अपनी स्थानीय परंपरा भी देखें", ticks, "/home/claude/ekadashi/vo.wav")
