import sys, json, numpy as np, soundfile as sf, os
os.chdir("/home/claude/tts"); sys.path.insert(0, "/home/claude/tts")
import importlib.util as _u; _s=_u.spec_from_file_location("ttsh","/home/claude/dhanteras/ttsh.py"); G=_u.module_from_spec(_s); _s.loader.exec_module(G)
G.SPK["n"] = ("priyamvada", 1.15, 1.0)
SR = G.SR
L = [
 ("n1", "बीस नवंबर, देवउठनी एकादशी! इस दिन विष्णु जी जागते हैं।", 0.1),
 ("n2", "सुबह स्नान करके दीया जलाएँ, और विष्णु जी को पीले फूल, फल और तुलसी दल चढ़ाएँ।", 0.3),
 ("n3", "विष्णु मंत्र जपें, व्रत कथा सुनें, और शाम को दीपदान करें।", 0.3),
 ("n4", "एकादशी तिथि, बीस नवंबर सुबह सात बजकर पंद्रह मिनट से। कमेंट में लिखिए, जय श्री हरि!", 0.3),
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
sf.write("/home/claude/ekadashi/vo.wav", out, SR)
json.dump(dict(total=total, segs=segs), open("/home/claude/ekadashi/vo.json", "w"), ensure_ascii=False, indent=1)
print(round(total, 2)); [print(s["id"], s["start"], s["end"]) for s in segs]
