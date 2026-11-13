# Daily Paper-Video Agent — भारत के त्योहार (@BharatKeTyohaar)

Every day at 5:15 PM IST, a scheduled run follows this file. It makes **one** 20–25 s paper cut-out Short for the Hindi/Bihar festival-info channel and hands it to the owner by about 5:40 PM, so it can go up at 6 PM.

## 0. Setup (every run starts on a fresh machine)
```bash
bash <repo>/setup.sh
```
This copies the kit to /home/claude (paperkit.py, make_voice.py, tts/, paper/, char_din/, dhanteras/, examples/), installs sherpa-onnx and downloads the Piper Hindi voices.

## 1. Pick today's topic (research)

**Choose a topic that people will search for in the next 1–5 days.** Priority order:
1. A festival, vrat or tithi coming in 1–5 days, e.g. "X kab hai", "puja vidhi", "samagri", "kya karein, kya na karein".
2. A weekly vrat for tomorrow: Somvar, Mangalvar, Guruvar, Shanivar, Ekadashi, Pradosh, Purnima or Amavasya.
3. A Bihar/UP tradition that is in season.

**Research and verification:**
- Use WebSearch/WebFetch. Hindi sources such as navbharatlive.com, prabhatkhabar.com and dekhopanchang.com work well.
- **Verify every date and time on the web.** Never use memory for dates, tithi times or muhurat.
- If sources disagree, say so on screen: "अपनी स्थानीय परंपरा भी देखें".

**Avoid repeats:** check `history.md` in this repo and don't repeat a topic made in the last 30 days.

## 2. Script rules (learned from channel analytics)

**Format:**
- 4 narration lines in total, about 20–25 s.
- Use a **checklist** format. Story/katha formats did worse: 37% stayed vs 46–70% for checklists.
- Line n1 is the **hook**: a surprising do/don't or a date question, e.g. "सोमवार को बेलपत्र मत तोड़ना!"
- n2 and n3 are 3–4 concrete items each, shown as ✔ tick cards or ✖ cross cards.
- n4 is the CTA: "कमेंट में लिखिए, जय …!"

**Writing the text:**
- Write numbers in words in the narration ("बीस नवंबर").
- On screen use Devanagari digits (२०).
- The font has **no `: - ? ! , …`**. Remove them from on-screen labels; use "७ बजकर १५ मिनट" instead of "7:15".

**Content limits:**
- Present religious claims as belief. Always show a disclaimer such as "मान्यताओं पर आधारित".
- Never promise money, health or children as a guaranteed outcome.
- Leave out suicide, death details and anything frightening; keep it family-friendly.

## 3. Build the video
1. Write `/home/claude/<slug>/lines.json`, then run `python3 /home/claude/make_voice.py /home/claude/<slug> /home/claude/<slug>/lines.json`.
2. Copy `examples/somvar/build.py` (or `examples/ekadashi/build.py`) to `/home/claude/<slug>/build.py`.
3. Change the paths, scenes, labels, sprites and `ticks` in the copy.
   - **Reusable sprites in paperkit.py:** sp_belpatra, sp_shivling, sp_lota_tilt, sp_onion_garlic, sp_sleep, sp_phalahar, sp_trishul, sp_vishnu, sp_flowers, sp_tulsi, sp_om, sp_book, sp_deeprow.
   - **From char_din via `CD.item`:** lota, kaddu, dal, bhaat, kheer, roti, clock, jal, thekua.
   - **From paper via `prop`:** sun, soop, havan, kheer, baby, palace.
   - **Paper dolls via `P.doll`:** raja, rani, rishi, devi.
   - **Helpers:** `tick_card`, `x_card`, `label`, `place`, `glowc`.
   - New sprites go in the build file. Draw them on a 520×520 canvas with PIL shapes.
4. Preview first: `python3 build.py 1,6,11,16,21`. Open `<slug>/prev.jpg` with Read and fix any overlaps or empty frames.
   - The hook must be fully visible at t=0.
   - Labels must not overlap the subtitle strip, which sits at about y=1795.
5. Render: `python3 build.py`. Check the duration with ffprobe and the loudness with `ffmpeg -af ebur128`, aiming for about -14 LUFS.

## 4. Deliver (no auto-upload)
1. Copy the mp4 to `/mnt/user-data/outputs/` and send it with SendUserFile, using status "proactive".
2. Send one SendUserMessage in Hinglish containing:
   - the topic;
   - **Title**, under 100 characters, ending with #Shorts;
   - **Description** with the ✅/❌ list, the comment question, the disclaimer and 6–8 hashtags including #BharatKeTyohaar;
   - **10 tags**, comma separated;
   - a **pinned-comment** line;
   - the sources;
   - a reminder: "6 PM पर अपलोड करने के लिए 'upload' लिखिए। Studio में भारत के त्योहार चैनल चुना हो।"
3. Do **not** upload to YouTube. Uploading needs the owner to pick the file on their Mac.
4. Save the video for later upload from any session:
   - Copy the mp4 to `videos/YYYY-MM-DD-<slug>.mp4` in this repo.
   - Write `videos/YYYY-MM-DD-<slug>.md` with the title, description, tags and pinned comment, exactly as sent.
5. Append one line to `history.md` (date | topic | title), then commit and push the files with `git -c push.negotiate=true push`.
