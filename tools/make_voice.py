"""Usage: python3 /home/claude/make_voice.py <workdir> <lines.json>
lines.json = [["n1","हुक लाइन...",0.1],["n2","...",0.3], ...]  (Hindi text, numbers in words, no ':' or '-')
Writes <workdir>/vo.wav and <workdir>/vo.json (segment timings)."""
import sys, json, os, importlib.util as u, numpy as np, soundfile as sf
wd, lines = sys.argv[1], json.load(open(sys.argv[2]))
os.makedirs(wd, exist_ok=True); os.chdir("/home/claude/tts"); sys.path.insert(0, "/home/claude/tts")
s = u.spec_from_file_location("ttsh", "/home/claude/dhanteras/ttsh.py"); G = u.module_from_spec(s); s.loader.exec_module(G)
G.SPK["n"] = ("priyamvada", 1.15, 1.0)
t = 0.0; segs = []; parts = []
for lid, txt, gap in lines:
    t += gap; x = G.say("n", txt)
    segs.append(dict(id=lid, text=txt, start=round(t, 3), end=round(t + len(x) / G.SR, 3))); parts.append((t, x)); t += len(x) / G.SR
total = t + 1.0; out = np.zeros(int(total * G.SR), np.float32)
for st, x in parts: out[int(st * G.SR):int(st * G.SR) + len(x)] += x
sf.write(f"{wd}/vo.wav", out, G.SR)
json.dump(dict(total=total, segs=segs), open(f"{wd}/vo.json", "w"), ensure_ascii=False, indent=1)
print(round(total, 2)); [print(s["id"], s["start"], s["end"]) for s in segs]
