import sys, json, numpy as np, soundfile as sf, os
os.chdir("/home/claude/tts"); sys.path.insert(0, "/home/claude/tts")
import importlib.util as _u; _s=_u.spec_from_file_location("ttsh","/home/claude/dhanteras/ttsh.py"); G=_u.module_from_spec(_s); _s.loader.exec_module(G)
G.SPK["n"] = ("priyamvada", 1.15, 1.0)
SR = G.SR
L = [
 ("n1", "दिवाली पर दुकानदार ये काम ज़रूर करें! पूरी लिस्ट देखिए।", 0.2),
 ("n2", "दिवाली के दिन दोपहर में, पूरी दुकान साफ़ करें, और दरवाज़े पर तोरण और दीये लगाएँ। साफ़ और रोशन दुकान में, ग्राहक भी खिंचे चले आते हैं।", 0.4),
 ("n3", "शाम को, लाल कपड़े वाली चौकी पर, लक्ष्मी जी और गणेश जी रखें, और सामने नया बही खाता और कलम रखें।", 0.35),
 ("n4", "बही के पहले पन्ने पर, कुमकुम से स्वास्तिक बनाएँ, और दोनों ओर, शुभ और लाभ लिखें।", 0.35),
 ("n5", "तिजोरी साफ़ करके, उत्तर दिशा में रखें। उसमें चाँदी का सिक्का, कौड़ी, और हल्दी की गाँठ रखें। ऐसी मान्यता है।", 0.35),
 ("n6", "पूजा का समय, दिल्ली में शाम पाँच बजकर इकतीस से, रात साढ़े दस बजे तक। अपने शहर का समय, स्क्रीन पर देखें।", 0.35),
 ("n7", "और हाँ, दीयों को कागज़ और सामान से दूर रखें। ईमानदारी की कमाई ही असली लक्ष्मी है। शुभ दीपावली!", 0.35),
]
t = 0.0; segs = []; parts = []
for lid, txt, gap in L:
    t += gap
    x = G.say("n", txt)
    segs.append(dict(id=lid, text=txt, start=round(t, 3), end=round(t + len(x) / SR, 3)))
    parts.append((t, x)); t += len(x) / SR
total = t + 1.6
out = np.zeros(int(total * SR), np.float32)
for st, x in parts:
    s = int(st * SR); out[s:s + len(x)] += x
sf.write("/home/claude/dukan/vo.wav", out, SR)
json.dump(dict(total=total, segs=segs), open("/home/claude/dukan/vo.json", "w"), ensure_ascii=False, indent=1)
print(round(total, 2)); [print(s["id"], s["start"], s["end"]) for s in segs]
