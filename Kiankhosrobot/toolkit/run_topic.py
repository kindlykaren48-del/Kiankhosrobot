"""Generic runner: content.json (+voice) -> reel/cover/caption using make_reel.py (GitHub engine).
Usage: python3 run_topic.py <workdir> <palette> <voice: female|male>  [--placeholder-audio]"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
work = os.path.abspath(sys.argv[1]); palette = sys.argv[2]; voice = sys.argv[3]
placeholder = "--placeholder-audio" in sys.argv
os.makedirs(work, exist_ok=True); os.chdir(work)
import make_reel, illus
c = json.load(open(os.path.join(work, "..", "content.json"), encoding="utf-8"))
make_reel.OUTDIR = os.path.abspath(os.path.join(work, "..", "out")); os.makedirs(make_reel.OUTDIR, exist_ok=True)

# extra palette: red + blue + phosphorescent green
make_reel.PALETTES.setdefault("redbluegreen", [((170, 18, 40), (240, 64, 72)), ((10, 52, 150), (36, 120, 235)),
    ((20, 140, 70), (120, 255, 110)), ((200, 30, 60), (255, 96, 110))])

# ---- illustrations: topic-specific scenes if available, otherwise generic icon scenes
scenes = {"fetal_hearing": [illus.scene_cover, illus.scene_womb, illus.scene_prefers_mom, illus.scene_notice, illus.scene_lullaby]}
paths = []
for i in range(5):
    p = f"ill_{i}.png"
    if c.get("scene") in scenes: scenes[c["scene"]][i]().save(p)
    else:
        ic = (c["slides"][min(i, 4)-1 if i else 0]["points"][0]["icon"]) if i < 5 else "star"
        illus.scene_generic(ic, i).save(p)
    paths.append(p)
illus.bg_cover("bg_cover.png")

# ---- voice (edge-tts, free): one mp3 per narration sentence
VOICES = {"female": "fa-IR-DilaraNeural", "male": "fa-IR-FaridNeural"}
for i, t in enumerate(c["narration"]):
    if placeholder:                                   # layout test only (no voice)
        secs = max(3.0, len(t.split())/2.2)
        subprocess.run([make_reel.FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(secs),
                        "-c:a", "libmp3lame", f"s{i}.mp3"], check=True, capture_output=True)
    else:
        open(f"s{i}.txt", "w", encoding="utf-8").write(t)
        subprocess.run([sys.executable, "-m", "edge_tts", "--voice", VOICES[voice], "--file", f"s{i}.txt",
                        "--write-media", f"s{i}.mp3"], check=True)

# ---- engine config
cfg = {"slug": c["slug"], "title_fa": c["title_fa"], "title_en": c["title_en"], "subtitle": c["subtitle"],
       "cta": c.get("cta", ""), "palette": palette, "cover_ill": paths[0],
       "slides": [(s["num"], s["title_fa"], s["title_en"], paths[k+1], [(p["icon"], p["text"]) for p in s["points"]])
                  for k, s in enumerate(c["slides"])]}
make_reel.build_all(cfg, target=25.0)
open(os.path.join(make_reel.OUTDIR, f"{c['slug']}_caption.txt"), "w", encoding="utf-8").write(
    c["caption"] + "\n\n" + " ".join(c.get("hashtags", [])))
print("OUT", make_reel.OUTDIR)
