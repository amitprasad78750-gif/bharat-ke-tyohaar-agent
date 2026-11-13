import sherpa_onnx, soundfile as sf, json, numpy as np, subprocess, os
V = {}
def tts(voice):
    if voice not in V:
        d = f"vits-piper-hi_IN-{voice}-medium"
        V[voice] = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f"{d}/hi_IN-{voice}-medium.onnx", tokens=f"{d}/tokens.txt", data_dir=f"{d}/espeak-ng-data"), num_threads=2)))
    return V[voice]
SR = 22050
# speaker -> (voice, speed, pitch)
SPK = {"heroine": ("priyamvada", 1.1, 1.06), "boy": ("pratham", 1.12, 1.32), "narr": ("rohan", 1.0, 0.9)}

def say(spk, text):
    v, sp, pitch = SPK[spk]
    a = tts(v).generate(text, sid=0, speed=sp)
    x = np.array(a.samples, dtype=np.float32)
    assert a.sample_rate == SR
    if pitch != 1.0:
        sf.write("/tmp/_i.wav", x, SR)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "/tmp/_i.wav", "-af", f"rubberband=pitch={pitch}", "/tmp/_o.wav"], check=True)
        x, _ = sf.read("/tmp/_o.wav", dtype="float32")
    nz = np.where(np.abs(x) > 0.01)[0]; x = x[max(0, nz[0] - 300):nz[-1] + 600]
    # compress internal silences longer than 0.28s
    fr = int(SR * 0.02); q = np.array([np.max(np.abs(x[i:i + fr])) for i in range(0, len(x), fr)])
    keep = []; run = 0
    for i, v in enumerate(q):
        if v < 0.02:
            run += 1
            if run * fr > SR * 0.28: continue
        else: run = 0
        keep.append(x[i * fr:(i + 1) * fr])
    x = np.concatenate(keep)
    return x / (np.max(np.abs(x)) + 1e-9) * 0.9

