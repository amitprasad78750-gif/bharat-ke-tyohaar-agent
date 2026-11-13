import sys, json, numpy as np, soundfile as sf, os
os.chdir("/home/claude/tts"); sys.path.insert(0, "/home/claude/tts")
import importlib.util as _u; _s=_u.spec_from_file_location("ttsh","/home/claude/dhanteras/ttsh.py"); G=_u.module_from_spec(_s); _s.loader.exec_module(G)
G.SPK["n"] = ("priyamvada", 1.15, 1.0)
SR = G.SR
L = [
 ("n1", "सोमवार को बेलपत्र मत तोड़ना! एक दिन पहले तोड़कर रख लें।", 0.1),
 ("n2", "सुबह स्नान करके शिवलिंग पर जल चढ़ाएँ। फिर तीन पत्तियों वाला साबुत बेलपत्र, चिकनी तरफ़ नीचे करके।", 0.3),
 ("n3", "दिन में एक बार सात्विक भोजन या फलाहार। प्याज़ लहसुन नहीं, और दिन में सोना नहीं।", 0.3),
 ("n4", "कमेंट में लिखिए, हर हर महादेव!", 0.3),
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
sf.write("/home/claude/somvar/vo.wav", out, SR)
json.dump(dict(total=total, segs=segs), open("/home/claude/somvar/vo.json", "w"), ensure_ascii=False, indent=1)
print(round(total, 2)); [print(s["id"], s["start"], s["end"]) for s in segs]
