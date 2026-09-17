"""
Reusable Instagram Reel builder (spec v2.1).
Outputs ONLY: <slug>_reel.mp4 (<=4MB, ~20s) + <slug>_cover.png
Set cfg["palette"] to override colors.
"""
import os, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from icons import icon
import imageio_ffmpeg


# ---------------- لایهٔ متن فارسی (HarfBuzz) ----------------
try:                       # شکل‌دهی درست حروف چسبان فارسی
    from fatext import FD as _FD
    HAVE_FATEXT = True
except Exception:          # نبود fatext → حالت قبلی (نیازمند libraqm)
    _FD = None
    HAVE_FATEXT = False


def _draw(image, mode=None):
    """جایگزین ImageDraw.Draw( ) که متن فارسی را درست می‌چیند."""
    if HAVE_FATEXT:
        return _FD(image, mode)
    return ImageDraw.Draw(image, mode) if mode else ImageDraw.Draw(image)


def _txt(image, xy, text, font, fill, anchor="mm"):
    if HAVE_FATEXT:
        return _FD(image).text(xy, text, font=font, fill=fill, anchor=anchor)
    return ImageDraw.Draw(image, "RGBA").text(xy, text, font=font, fill=fill,
                                       anchor=anchor, **KW)


def _bbox(d, xy, text, font, anchor="mm"):
    if HAVE_FATEXT:
        return d.textbbox(xy, text, font=font, anchor=anchor)
    return d.textbbox(xy, text, font=font, anchor=anchor, **KW)
# -------------------------------------------------------------


FF = imageio_ffmpeg.get_ffmpeg_exe()
FTDIR = "/home/user/fonttmp/fonts/ttf/"
BLACK = FTDIR + "Vazirmatn-Black.ttf"
BOLD = FTDIR + "Vazirmatn-Bold.ttf"
REG = FTDIR + "Vazirmatn-Medium.ttf"
W, H, FPS = 1080, 1920, 30
KW = dict(language="fa", direction="rtl")
OUTDIR = "/home/user/Kiankhosrobot"

PALETTES = {
    "purple":     [((124,58,183),(233,64,140)), ((219,68,55),(247,151,30)),
                   ((0,150,199),(72,202,228)),  ((56,142,60),(139,195,74))],
    "greenred":   [((13,92,62),(34,150,94)),    ((150,20,30),(214,58,48)),
                   ((16,105,70),(70,168,90)),   ((168,28,36),(232,88,60))],
    "orangeteal": [((214,106,18),(247,166,54)), ((10,110,124),(38,178,190)),
                   ((222,120,26),(250,180,70)), ((12,122,132),(56,196,200))],
    "redblue":    [((156,16,28),(220,52,52)),   ((14,54,126),(38,110,200)),
                   ((168,22,34),(232,72,64)),   ((16,66,140),(52,132,214))],
    "redgreen":   [((158,18,30),(220,56,52)),   ((14,96,64),(40,158,96)),
                   ((170,24,36),(232,76,62)),   ((16,108,72),(60,176,108))],
    "wineamber": [((74,10,34),(158,28,62)), ((122,66,8),(214,148,32)),
                  ((92,14,44),(176,40,80)), ((136,80,10),(230,170,54))],
    "aurora": [((124,58,236),(186,130,255)), ((14,165,183),(86,232,235)), ((236,72,120),(255,150,180)), ((234,179,8),(255,222,110))],
    "neonmosaic": [((0,200,190),(90,255,235)), ((255,90,120),(255,160,175)), ((255,190,40),(255,225,120)), ((140,110,255),(190,170,255))],
    "neonpurple": [((168,85,247),(216,160,255)), ((34,211,238),(140,245,255)), ((244,114,182),(255,175,215)), ((250,204,21),(255,232,120))],
    "neon": [((232,170,20),(255,214,70)), ((30,120,230),(90,190,255)),
             ((36,190,120),(120,240,160)), ((240,150,30),(255,200,90))],
    "nuclear": [((28,30,16),(180,170,20)), ((10,48,40),(40,190,120)),
                ((40,38,10),(214,196,30)), ((8,54,52),(28,178,160))],
    "kiddo": [((240,120,40),(255,196,60)), ((36,150,200),(90,215,235)),
              ((196,60,150),(255,140,190)), ((60,170,90),(160,225,110))],
    "purplegreen": [((52,16,98),(118,54,186)), ((14,104,70),(46,166,104)),
                    ((66,22,120),(138,72,206)), ((16,118,78),(60,184,118))],
    "redmustard": [((132,14,28),(212,52,60)), ((132,96,10),(224,178,44)),
                   ((150,18,34),(228,70,74)), ((148,108,14),(238,196,66))],
    "purplemustard": [((58,18,104),(122,58,190)), ((132,96,10),(224,178,44)),
                      ((72,24,126),(142,76,210)), ((148,108,14),(238,196,66))],
    "bluegreen": [((8,44,120),(30,104,210)), ((18,112,64),(120,240,90)),
                  ((10,58,146),(46,130,235)), ((24,126,70),(146,250,110))],
    "greenpink":  [((12,110,72),(44,168,104)),  ((176,26,104),(232,74,150)),
                   ((14,120,80),(62,182,120)),  ((186,30,112),(240,92,164))],
}


def dur(f):
    o = subprocess.run([FF, "-i", f], capture_output=True).stderr.decode()
    h, m, s = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', o).groups()
    return float(h)*3600 + float(m)*60 + float(s)


def cover_fill(im, w, h):
    r = max(w/im.width, h/im.height)
    im = im.resize((max(w, int(im.width*r)), max(h, int(im.height*r))), Image.LANCZOS)
    l, t = (im.width-w)//2, (im.height-h)//2
    return im.crop((l, t, l+w, t+h))


def flatten(path):
    src = Image.open(path)
    base = Image.new("RGB", src.size, (255, 255, 255))
    if src.mode in ("RGBA", "LA"):
        base.paste(src.convert("RGB"), (0, 0), src.convert("RGBA").split()[-1])
    else:
        base.paste(src.convert("RGB"), (0, 0))
    return base


def make_music(path="bgm.wav"):
    sr, bpm, bars = 44100, 112, 8
    beat = 60/bpm
    total = int(sr*beat*4*bars)
    out = np.zeros(total)

    def note(f, st, d_, amp=0.2, kind='saw'):
        n0, n1 = int(st*sr), min(int((st+d_)*sr), total)
        if n1 <= n0: return
        tt = np.arange(n1-n0)/sr
        s = (sum(np.sin(2*np.pi*f*k*tt)/k for k in range(1, 7))*0.5 if kind == 'saw'
             else np.sin(2*np.pi*f*tt) + 0.4*np.sin(4*np.pi*f*tt))
        out[n0:n1] += amp*s*np.exp(-tt*3.2)*(1-np.exp(-tt*180))

    def kick(st, amp=0.55):
        n0, n1 = int(st*sr), min(int(st*sr)+int(0.16*sr), total)
        tt = np.arange(n1-n0)/sr
        out[n0:n1] += amp*np.sin(2*np.pi*(150*np.exp(-tt*28)+45)*tt)*np.exp(-tt*13)

    def hat(st, amp=0.13):
        n0, n1 = int(st*sr), min(int(st*sr)+int(0.05*sr), total)
        tt = np.arange(n1-n0)/sr
        out[n0:n1] += amp*np.random.randn(n1-n0)*np.exp(-tt*60)

    sc = {'C':261.63,'D':293.66,'E':329.63,'F':349.23,'G':392.0,'A':440.0,'B':493.88,
          'C5':523.25,'D5':587.33,'E5':659.25,'G5':784.0,'A5':880.0}
    prog = [['F','A','C5'], ['G','B','D5'], ['A','C5','E5'], ['C','E','G']]
    mel = [['C5','E5','G5','E5'], ['D5','G5','B','D5'], ['E5','A5','E5','C5'], ['G5','E5','C5','G5']]
    for bar in range(bars):
        b0 = bar*4*beat
        for f in prog[bar % 4]:
            note(sc[f]/2, b0, beat*3.6, 0.09, 'sine')
        for i, nm in enumerate(mel[bar % 4]):
            note(sc[nm], b0+i*beat, beat*0.95, 0.16)
        for i in range(4):
            kick(b0+i*beat); hat(b0+i*beat+beat/2); hat(b0+i*beat+beat/4, 0.07)
    out /= np.max(np.abs(out))*1.05
    f = int(sr*0.4)
    out[:f] *= np.linspace(0, 1, f); out[-f:] *= np.linspace(1, 0, f)
    w = wave.open(path, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((out*32767).astype('<i2').tobytes()); w.close()



def top_scrim(img, y_end=780, top_a=190, base_a=70):
    """پردهٔ گرادیانی تیره در بالای کاور تا تیتر خوانا بماند."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(0, y_end):
        f = y / float(y_end)
        a = int(base_a + (top_a - base_a) * (1 - f) ** 1.25)
        od.line([(0, y), (W, y)], fill=(12, 2, 28, a))
    od.rectangle([0, y_end, W, H], fill=(12, 2, 28, base_a // 2))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def grad_text(base, txt, font, xy, c1, c2, anchor="mm"):
    tmp = Image.new("L", (W, H), 0)
    _txt(tmp, xy, txt, font=font, fill=255, anchor=anchor)
    bb = tmp.getbbox()
    g = Image.new("RGB", (W, H), c2); gd = _draw(g)
    y0, y1 = bb[1], bb[3]
    for y in range(y0, y1+1):
        f = (y-y0)/max(1, y1-y0)
        gd.line([(0, y), (W, y)], fill=tuple(int(c1[k]+(c2[k]-c1[k])*f) for k in range(3)))
    base.paste((0, 0, 0), (0, 0), tmp.filter(ImageFilter.GaussianBlur(14)))
    base.paste(g, (0, 0), tmp)


def make_cover(cfg):
    bg = cover_fill(Image.open("bg_cover.png").convert("RGB"), W, H)
    cov = top_scrim(bg); d = _draw(cov, "RGBA")
    fa = cfg["title_fa"]
    size = 120 if len(fa) <= 12 else (104 if len(fa) <= 16 else 88)
    grad_text(cov, fa, ImageFont.truetype(BLACK, size), (W/2, 330), (255, 236, 170), (212, 148, 20))
    d = _draw(cov, "RGBA")
    en = cfg["title_en"].upper()
    esz = 58 if len(en) <= 18 else (46 if len(en) <= 24 else 40)
    d.text((W/2, 460), en, font=ImageFont.truetype(BOLD, esz), fill=(255, 255, 255, 235), anchor="mm")
    sub = cfg["subtitle"]
    hw = min(430, 26 + len(sub)*17)
    d.rounded_rectangle([W/2-hw, 540, W/2+hw, 630], 45, fill=(255, 255, 255, 38),
                        outline=(255, 215, 120, 220), width=3)
    d.text((W/2, 585), sub, font=ImageFont.truetype(BOLD, 44), fill=(255, 235, 190), anchor="mm")

    # cover illustration card
    ci = cfg.get("cover_ill", cfg["slides"][0][3])
    cw, chh, cy0 = 860, 1075, 700
    cx0 = (W-cw)//2
    card = cover_fill(flatten(ci), cw, chh)
    mask = Image.new("L", (cw, chh), 0)
    _draw(mask).rounded_rectangle([0, 0, cw, chh], 48, fill=255)
    d.rounded_rectangle([cx0-10, cy0-10, cx0+cw+10, cy0+chh+10], 58, fill=(255, 255, 255, 95))
    cov.paste(card, (cx0, cy0), mask)
    d = _draw(cov, "RGBA")
    d.rounded_rectangle([W/2-210, 1855, W/2+210, 1895], 20, fill=(255, 255, 255, 70))
    cov.save("f_cover.png")


def make_slide(idx, cfg, PAL):
    num, fa, en, ill, items = cfg["slides"][idx]
    c1, c2 = PAL[idx]
    img = Image.new("RGB", (W, H)); d = _draw(img)
    for y in range(H):
        f = y/H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[k]+(c2[k]-c1[k])*f) for k in range(3)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = _draw(ov)
    for (cx, cy, r, a) in [(150,300,260,40),(950,1500,320,35),(900,250,180,30),(200,1700,240,28)]:
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 255, a))
    ov = ov.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = _draw(img, "RGBA")

    # ZONE 1: header
    d.ellipse([70, 108, 230, 268], fill=(255, 255, 255, 240))
    d.text((150, 188), num, font=ImageFont.truetype(BLACK, 88), fill=c1, anchor="mm")
    d.text((W-90, 150), fa, font=ImageFont.truetype(BLACK, 76), fill=(255, 255, 255), anchor="ra")
    d.text((W-90, 252), en.upper(), font=ImageFont.truetype(BOLD, 32), fill=(255, 255, 255, 215), anchor="ra")

    # ZONE 2: text box right under the header
    n, lh = len(items), 98
    bx0, bx1 = 70, W-70
    for k in range(4):
        x = W/2 + (k-1.5)*60
        d.ellipse([x-13, 292, x+13, 318], fill=(255, 255, 255, 255 if k == idx else 90))
    by0 = 348; by1 = by0 + n*lh + 56
    d.rounded_rectangle([bx0, by0, bx1, by1], 44, fill=(12, 6, 30, 225), outline=(255, 255, 255, 60), width=3)
    fb = ImageFont.truetype(BOLD, 42)
    y = by0 + 28
    for ic, tx in items:
        d.ellipse([bx0+34, y+2, bx0+92, y+60], fill=(255, 255, 255, 240))
        ic_im = icon(ic, 38, (30, 22, 60))
        img.paste(ic_im, (bx0+44, int(y+12)), ic_im)
        d = _draw(img, "RGBA")
        d.text((bx1-40, y+31), tx, font=fb, fill=(255, 255, 255), anchor="rm")
        y += lh

    # ZONE 3: image card below the text, nothing drawn on it
    cw, chh = 760, 950
    cy0 = by1 + 48
    cx0 = (W-cw)//2
    card = cover_fill(flatten(ill), cw, chh)
    mask = Image.new("L", (cw, chh), 0)
    _draw(mask).rounded_rectangle([0, 0, cw, chh], 44, fill=255)
    d.rounded_rectangle([cx0-8, cy0-8, cx0+cw+8, cy0+chh+8], 52, fill=(255, 255, 255, 80))
    img.paste(card, (cx0, cy0), mask)
    d = _draw(img, "RGBA")
    img.save(f"f_s{idx+1}.png")


def make_cta(cfg):
    cta = cover_fill(Image.open("bg_cover.png").convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(6))
    d = _draw(cta, "RGBA"); d.rectangle([0, 0, W, H], fill=(15, 0, 35, 150))
    grad_text(cta, "ذخیره کن!", ImageFont.truetype(BLACK, 120), (W/2, 660), (255, 240, 180), (215, 150, 25))
    d = _draw(cta, "RGBA")
    d.text((W/2, 810), cfg.get("cta", "این ویدیو را برای خانواده و کادر درمان بفرست"),
           font=ImageFont.truetype(BOLD, 46), fill=(255, 255, 255, 240), anchor="mm")
    d.rounded_rectangle([W/2-300, 930, W/2+300, 1035], 50, fill=(255, 255, 255, 235))
    d.text((W/2, 982), "ذخیره  •  اشتراک‌گذاری", font=ImageFont.truetype(BOLD, 42),
           fill=(120, 20, 90), anchor="mm")
    d.text((W/2, 1160), "پیجم را دنبال کن برای آموزش‌های بیشتر",
           font=ImageFont.truetype(REG, 38), fill=(255, 255, 255, 190), anchor="mm")
    cta.save("f_cta.png")


def _enc(args):
    from concurrent.futures import ThreadPoolExecutor
    def _run(a):
        subprocess.run(a, check=True, capture_output=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(_run, args))


def render(cfg, target=25.0):
    slug = cfg["slug"]
    OUT = f"{OUTDIR}/{slug}_reel.mp4"
    raw = [dur(f"s{i}.mp3") for i in range(5)]
    GAP, CTA = 0.10, 1.6
    tempo = max(1.0, min(round(sum(raw)/(target-CTA-5*GAP), 3), 1.55))
    V = []
    for i in range(5):
        o = f"t{i}.mp3"
        subprocess.run([FF, "-y", "-i", f"s{i}.mp3", "-filter:a", f"atempo={tempo}", "-b:a", "96k", o],
                       check=True, capture_output=True)
        V.append((o, dur(o)))
    print("tempo", tempo, "| voice sum", round(sum(x[1] for x in V), 2))
    parts = []

    def seg(img, aud, t, out, zin=True, adelay=90, atrim=None, fout=False):
        z = "min(zoom+0.0009,1.10)" if zin else "if(eq(on,0),1.10,max(zoom-0.0009,1.0))"
        vf = (f"[0:v]scale={W}:{H},zoompan=z='{z}':d={int(t*FPS)}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},fade=in:0:5")
        if fout:
            vf += f",fade=out:{max(0,int(t*FPS)-10)}:10"
        vf += "[v]"
        af = (f"[1:a]{'atrim='+atrim+',asetpts=N/SR/TB,' if atrim else ''}"
              f"adelay={adelay}|{adelay},apad,atrim=0:{t},asetpts=N/SR/TB[a]")
        subprocess.run([FF, "-y", "-loop", "1", "-i", img, "-i", aud, "-filter_complex", vf+";"+af,
                        "-map", "[v]", "-map", "[a]", "-t", str(t), "-r", str(FPS), "-pix_fmt", "yuv420p",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "26",
                        "-c:a", "aac", "-b:a", "96k", "-ar", "44100", out],
                       check=True, capture_output=True)
        parts.append(out)

    d4 = V[4][1]; sp = round(d4*0.58, 2)
    jobs = [("f_cover.png", V[0][0], round(V[0][1]+GAP, 2), "g0.mp4", True),
            ("f_s4.png", V[4][0], round(sp+0.08, 2), "g4.mp4", True)]
    for i in range(1, 4):
        jobs.append((f"f_s{i}.png", V[i][0], round(V[i][1]+GAP, 2), f"g{i}.mp4", i % 2 == 0))
    jobs.append(("f_cta.png", V[4][0], round(d4-sp+CTA*0.55, 2), "g5.mp4",
                 dict(zin=True, adelay=0, atrim=f"{sp}:{d4}", fout=True)))
    for j in jobs:
        if isinstance(j[4], bool):
            seg(j[0], j[1], j[2], j[3], j[4])
        else:
            seg(j[0], j[1], j[2], j[3], **j[4])

    open("gl.txt", "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", "gl.txt", "-c", "copy", "g_all.mp4"],
                   check=True, capture_output=True)
    T = dur("g_all.mp4")
    subprocess.run([FF, "-y", "-i", "g_all.mp4", "-af", "loudnorm=I=-14:TP=-1.5",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "mix.mp4"],
                   check=True, capture_output=True)
    for p in (1, 2):
        cmd = [FF, "-y", "-i", "mix.mp4", "-c:v", "libx264", "-b:v", "1050k", "-pass", str(p),
               "-passlogfile", "plog", "-preset", "slow", "-profile:v", "high", "-level", "4.0",
               "-pix_fmt", "yuv420p", "-g", "60"]
        cmd += (["-an", "-f", "mp4", "/dev/null"] if p == 1 else
                ["-c:a", "aac", "-b:a", "96k", "-ar", "44100", "-movflags", "+faststart", OUT])
        subprocess.run(cmd, check=True, capture_output=True)
    import shutil
    shutil.copy("f_cover.png", f"{OUTDIR}/{slug}_cover.png")
    print("DONE", round(dur(OUT), 2), "s |", round(os.path.getsize(OUT)/1048576, 2), "MB")
    return OUT


def build_all(cfg, target=25.0):
    global _NEON_BASE, _NEON_ARC, _NEON_MOSAIC
    _NEON_BASE = tuple(cfg.get("neon_base", (8, 8, 10)))
    _NEON_ARC = tuple(cfg.get("neon_arc", (255, 140, 30, 26)))
    _NEON_MOSAIC = bool(cfg.get("neon_mosaic", False))
    PAL = cfg.get("palette") if isinstance(cfg.get("palette"), list) \
        else PALETTES.get(cfg.get("palette", "purple"), PALETTES["purple"])
    if cfg.get("style") == "neon":
        neon_cover(cfg, PAL)
        for i in range(4):
            neon_slide(i, cfg, PAL)
        neon_cta(cfg, PAL)
    else:
        make_cover(cfg)
        for i in range(4):
            make_slide(i, cfg, PAL)
        make_cta(cfg)
    return render(cfg, target)


# ============================ NEON STYLE ============================

_NEON_BASE = (8, 8, 10)
_NEON_MOSAIC = False
_NEON_ARC = (255, 140, 30, 26)


def _neon_bg(seed_cols):
    img = Image.new("RGB", (W, H), _NEON_BASE)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = _draw(ov)
    spots = [(120, 240, 520), (960, 700, 460), (180, 1500, 560), (940, 1820, 480)]
    for i, (cx, cy, r) in enumerate(spots):
        c = seed_cols[i % len(seed_cols)]
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(c[0], c[1], c[2], 46))
    ov = ov.filter(ImageFilter.GaussianBlur(150))
    img = Image.alpha_composite(img.convert("RGBA"), ov)
    d = _draw(img, "RGBA")
    if _NEON_MOSAIC:
        import random as _rnd
        r = _rnd.Random(7)
        mo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        md = _draw(mo, "RGBA")
        TS = 108
        for gy in range(0, H, TS):
            for gx in range(0, W, TS):
                c = seed_cols[(gx//TS + gy//TS) % len(seed_cols)]
                a = r.choice([0, 0, 0, 0, 22, 34, 46])
                if a:
                    md.rounded_rectangle([gx+5, gy+5, gx+TS-5, gy+TS-5], 16,
                                         fill=(c[0], c[1], c[2], a))
                md.rounded_rectangle([gx+5, gy+5, gx+TS-5, gy+TS-5], 16,
                                     outline=(c[0], c[1], c[2], 46), width=2)
        mo.putalpha(mo.getchannel("A").point(lambda v: int(v*0.42)))
        img = Image.alpha_composite(img, mo)
        d = _draw(img, "RGBA")
    for k in range(5):
        y = 120 + k*430
        d.arc([-420, y, W+420, y+560], 200, 340, fill=_NEON_ARC, width=6)
    return img.convert("RGB")


def _neon_card(d, box, accent, radius=34, fill=(18, 18, 22, 240), glow=True):
    x0, y0, x1, y1 = box
    if glow:
        for g in (16, 11, 6):
            a = int(16 + (16-g)*4)
            d.rounded_rectangle([x0-g, y0-g, x1+g, y1+g], radius+g,
                                outline=(accent[0], accent[1], accent[2], a), width=3)
    d.rounded_rectangle(box, radius, fill=fill, outline=accent, width=4)


def neon_cover(cfg, PAL):
    a1 = PAL[0][1]; a2 = PAL[1][1]
    cov = _neon_bg([PAL[0][1], PAL[1][1], PAL[2][1], PAL[3][1]])
    d = _draw(cov, "RGBA")

    fa = cfg["title_fa"]
    size = 118 if len(fa) <= 13 else (100 if len(fa) <= 18 else 86)
    f = ImageFont.truetype(BLACK, size)
    bb = _bbox(d, (W/2, 300), fa, f, "mm")
    pad = 34
    _neon_card(d, [bb[0]-pad, bb[1]-22, bb[2]+pad, bb[3]+22], a1, 28,
               fill=(a1[0], a1[1], a1[2], 250), glow=True)
    d.text((W/2, 300), fa, font=f, fill=(10, 10, 12), anchor="mm")

    sub = cfg["subtitle"]
    fs = ImageFont.truetype(BOLD, 46)
    bb = _bbox(d, (W/2, 432), sub, fs, "mm")
    _neon_card(d, [bb[0]-30, bb[1]-18, bb[2]+30, bb[3]+18], a2, 24,
               fill=(16, 16, 20, 235), glow=True)
    d.text((W/2, 432), sub, font=fs, fill=(255, 255, 255), anchor="mm")

    en = cfg["title_en"].upper()
    d.text((W/2, 528), en, font=ImageFont.truetype(BOLD, 34),
           fill=(255, 255, 255, 165), anchor="mm")

    ci = cfg.get("cover_ill", cfg["slides"][0][3])
    cw, chh, cy0 = 880, 1010, 590
    cx0 = (W-cw)//2
    card = cover_fill(flatten(ci), cw, chh)
    mask = Image.new("L", (cw, chh), 0)
    _draw(mask).rounded_rectangle([0, 0, cw, chh], 40, fill=255)
    _neon_card(d, [cx0-14, cy0-14, cx0+cw+14, cy0+chh+14], a1, 52,
               fill=(14, 14, 18, 255), glow=True)
    cov.paste(card, (cx0, cy0), mask)
    d = _draw(cov, "RGBA")

    tags = cfg.get("cover_tags", [])[:4]
    n_t = len(tags)
    ty = 1880 - (n_t-1)*66 - 40
    fx = ImageFont.truetype(BOLD, 34)
    for i, t in enumerate(tags):
        col = PAL[i % 4][1]
        bb = _bbox(d, (W/2, ty), t, fx, "mm")
        _neon_card(d, [bb[0]-26, bb[1]-14, bb[2]+26, bb[3]+14], col, 22,
                   fill=(16, 16, 20, 240), glow=False)
        d.text((W/2, ty), t, font=fx, fill=col, anchor="mm")
        ty += 66
    cov.save("f_cover.png")


def neon_slide(idx, cfg, PAL):
    num, fa, en, ill, items = cfg["slides"][idx]
    acc = PAL[idx][1]
    img = _neon_bg([PAL[idx][1], PAL[(idx+1) % 4][1], PAL[idx][0], PAL[(idx+2) % 4][1]])
    d = _draw(img, "RGBA")

    # header
    _neon_card(d, [70, 104, 238, 272], acc, 46, fill=(acc[0], acc[1], acc[2], 250))
    d.text((154, 188), num, font=ImageFont.truetype(BLACK, 86),
           fill=(10, 10, 12), anchor="mm")
    d.text((W-90, 148), fa, font=ImageFont.truetype(BLACK, 74),
           fill=(255, 255, 255), anchor="ra")
    d.text((W-90, 250), en.upper(), font=ImageFont.truetype(BOLD, 30),
           fill=(acc[0], acc[1], acc[2], 245), anchor="ra")

    for k in range(4):
        x = W/2 + (k-1.5)*58
        if k == idx:
            d.ellipse([x-14, 300, x+14, 328], fill=acc)
        else:
            d.ellipse([x-11, 303, x+11, 325], fill=(255, 255, 255, 60))

    # bullet cards
    n = len(items)
    bh, gap = 112, 18
    by0 = 356
    fb = ImageFont.truetype(BOLD, 40)
    y = by0
    for i, (ic, tx) in enumerate(items):
        col = PAL[(idx+i) % 4][1]
        _neon_card(d, [70, y, W-70, y+bh], col, 28, fill=(18, 18, 23, 242), glow=False)
        d.ellipse([104, y+27, 162, y+85], fill=col)
        ic_im = icon(ic, 36, (12, 12, 14))
        img.paste(ic_im, (115, int(y+38)), ic_im)
        d = _draw(img, "RGBA")
        d.text((W-112, y+bh/2), tx, font=fb, fill=(255, 255, 255), anchor="rm")
        y += bh + gap

    cy0 = y + 28
    cw = 880
    chh = min(1080, H - cy0 - 70)
    cx0 = (W-cw)//2
    card = cover_fill(flatten(ill), cw, chh)
    mask = Image.new("L", (cw, chh), 0)
    _draw(mask).rounded_rectangle([0, 0, cw, chh], 40, fill=255)
    _neon_card(d, [cx0-14, cy0-14, cx0+cw+14, cy0+chh+14], acc, 52,
               fill=(14, 14, 18, 255), glow=True)
    img.paste(card, (cx0, cy0), mask)
    img.save(f"f_s{idx+1}.png")


def neon_cta(cfg, PAL):
    a1 = PAL[0][1]; a2 = PAL[1][1]
    cta = _neon_bg([PAL[0][1], PAL[1][1], PAL[2][1], PAL[3][1]])
    d = _draw(cta, "RGBA")
    f = ImageFont.truetype(BLACK, 122)
    bb = d.textbbox((W/2, 700), "ذخیره کن!", font=f, anchor="mm")
    _neon_card(d, [bb[0]-44, bb[1]-28, bb[2]+44, bb[3]+28], a1, 34,
               fill=(a1[0], a1[1], a1[2], 250))
    d.text((W/2, 700), "ذخیره کن!", font=f, fill=(10, 10, 12), anchor="mm")
    d.text((W/2, 866), cfg.get("cta", ""), font=ImageFont.truetype(BOLD, 44),
           fill=(255, 255, 255, 240), anchor="mm")
    _neon_card(d, [W/2-320, 968, W/2+320, 1078], a2, 44, fill=(16, 16, 20, 240))
    d.text((W/2, 1023), "ذخیره  •  اشتراک‌گذاری", font=ImageFont.truetype(BOLD, 42),
           fill=a2, anchor="mm")
    d.text((W/2, 1210), "پیجم را دنبال کن برای آموزش‌های بیشتر",
           font=ImageFont.truetype(REG, 38), fill=(255, 255, 255, 185), anchor="mm")
    cta.save("f_cta.png")
