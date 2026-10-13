"""
make_rostam_video.py — ساخت ویدیوی سینمایی رستم از چهار نمای ثابت
افکت‌ها: حرکت آرام دوربین (Ken Burns)، لرزش و فلاش ضربه، جرقه‌های شنـاور،
مِه گرمایی، وینیت، دانهٔ فیلم، محو شدن ابتدا/انتها.  بیت‌ریت بدون صدا.
"""
import os
import numpy as np
from PIL import Image
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
OUT = os.path.join(HERE, "rostam_duel.mp4")
PAD = 1.18                      # حاشیهٔ بزرگ‌نمایی برای حرکت دوربین


# ------------------------------------------------------------------ sources
def load_src(name):
    im = Image.open(os.path.join(HERE, name)).convert("RGB")
    s = max(W * PAD / im.width, H * PAD / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


SRC = {}


def src(name):
    if name not in SRC:
        SRC[name] = load_src(name)
    return SRC[name]


# ------------------------------------------------------------------ look-up
VIG = None


def vig_mask():
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:H, 0:W]
        dx = (x - W / 2) / (W / 2)
        dy = (y - H / 2) / (H / 2)
        r = np.sqrt(dx * dx * 0.95 + dy * dy * 0.95)
        v = np.clip(1.0 - 0.42 * np.clip(r - 0.35, 0, None) ** 1.7, 0.35, 1.0)
        VIG = (v * 255).astype(np.uint16)
    return VIG


def grain(rng):
    return rng.integers(-3, 4, (H, W, 1), dtype=np.int16)


# ------------------------------------------------------------------ embers
SPRITES = {}
COLORS = [(255, 176, 70), (255, 132, 34), (255, 220, 150), (150, 235, 255)]


def sprite(r):
    if r not in SPRITES:
        s = r * 4 + 1
        yy, xx = np.mgrid[-s:s + 1, -s:s + 1]
        d = np.sqrt(xx ** 2 + yy ** 2) / (r * 2.2)
        SPRITES[r] = np.clip(1.2 - d, 0, 1) ** 2.1
    return SPRITES[r]


class Embers:
    def __init__(self, seed=4, n=150):
        self.rng = np.random.default_rng(seed)
        self.n = n
        self.x = self.rng.uniform(0, W, n)
        self.y = self.rng.uniform(0, H, n)
        self.vy = -self.rng.uniform(18, 78, n)
        self.vx = self.rng.uniform(-16, 16, n)
        self.r = self.rng.choice([1, 1, 2, 2, 3], n)
        self.c = self.rng.integers(0, len(COLORS), n)
        self.ph = self.rng.uniform(0, 6.28, n)

    def step(self, dt, t, boost=1.0):
        self.y += self.vy * dt
        self.x += self.vx * dt + np.sin(t * 1.1 + self.ph) * 0.6
        idx = np.flatnonzero(self.y < -20)
        if idx.size:
            k = idx.size
            self.y[idx] = H + self.rng.uniform(5, 90, k)
            self.x[idx] = self.rng.uniform(0, W, k)
            self.r[idx] = self.rng.choice([1, 1, 2, 2, 3], k)
            self.c[idx] = self.rng.integers(0, len(COLORS), k)
            self.ph[idx] = self.rng.uniform(0, 6.28, k)
        return boost

    def draw(self, frame_i16, t, boost=1.0):
        flick = 0.72 + 0.28 * np.sin(t * 6.0 + self.ph)
        for i in range(self.n):
            r = int(self.r[i])
            sp = sprite(r) * (0.85 * flick[i] * boost)
            x, y = int(self.x[i]), int(self.y[i])
            if x < -r * 3 or x > W + r * 3 or y < -r * 3 or y > H + r * 3:
                continue
            x0, x1 = max(0, x - r * 2), min(W, x + r * 2 + 1)
            y0, y1 = max(0, y - r * 2), min(H, y + r * 2 + 1)
            if x1 <= x0 or y1 <= y0:
                continue
            sx0, sy0 = x0 - (x - r * 2), y0 - (y - r * 2)
            blk = sp[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
            col = np.array(COLORS[int(self.c[i])], dtype=np.float32)
            add = (blk[:, :, None] * col[None, None, :]).astype(np.int16)
            frame_i16[y0:y1, x0:x1] += add


EMB = Embers()


# ------------------------------------------------------------------ cameras
SEGS = [
    # (name, frames, zoom0, zoom1, panx0, panx1, pany0, pany1, shake, flash, boost)
    ("shot1_wide.png",    168, 1.02, 1.11,  0.14, 0.02, -0.06, 0.06, 0.0, 0.0, 1.0),
    ("shot3_closeup.png", 150, 1.04, 1.16, -0.03, 0.03, -0.02, 0.03, 0.0, 0.0, 1.35),
    ("shot4_raise.png",   168, 1.02, 1.13,  0.02, -0.04, 0.07, -0.03, 0.0, 0.0, 1.15),
    ("shot2_impact.png",  168, 1.17, 1.03, -0.02, 0.03, -0.04, 0.05, 1.0, 1.0, 1.7),
    ("shot1_wide.png",    162, 1.12, 1.02,  0.0, -0.03, -0.02, 0.04, 0.0, 0.0, 0.9),
]
TOTAL = sum(s[1] for s in SEGS)
XFADE = 6                                    # فریم‌های محو متقابل بین نماها


def ease(t):                                 # smoothstep
    return t * t * (3 - 2 * t)


def crop_frame(img, zoom, dx, dy):
    w = int(W / zoom)
    h = int(H / zoom)
    mx = (img.width - w) / 2
    my = (img.height - h) / 2
    x = int(round(mx + dx * mx))
    y = int(round(my + dy * my))
    x = max(0, min(img.width - w, x))
    y = max(0, min(img.height - h, y))
    win = img.crop((x, y, x + w, y + h))
    return win.resize((W, H), Image.BILINEAR)


def render_seg(seg_i, t_local, t_global, rng):
    name, n, z0, z1, px0, px1, py0, py1, shake, flash, boost = SEGS[seg_i]
    u = ease(min(1.0, max(0.0, t_local / max(1e-6, (n - 1)))))
    zoom = z0 + (z1 - z0) * u
    dx = px0 + (px1 - px0) * u
    dy = py0 + (py1 - py0) * u

    # مِه گرمایی: نوسان آرام کادر
    dx += 0.010 * np.sin(t_global * 1.9 + 1.1)
    dy += 0.008 * np.sin(t_global * 1.4)

    fx = 0.0
    if shake > 0:                            # لرزش ضربه
        amp = shake * 0.055 * np.exp(-t_local / 0.34)
        dx += amp * np.sin(t_global * 61.0)
        dy += amp * np.cos(t_global * 47.0)
    if flash > 0:                            # فلاش ضربه
        fx = flash * 0.75 * np.exp(-t_local / 0.085)

    im = crop_frame(src(name), zoom, dx, dy)
    frame = np.asarray(im, dtype=np.int16)

    EMB.step(1.0 / FPS, t_global, boost)
    EMB.draw(frame, t_global, boost)

    if fx > 0.01:                            # نور سفید لحظهٔ ضربه
        frame = frame + (fx * 120).astype(np.int16)

    frame += grain(rng)                      # دانهٔ فیلم
    frame = np.clip(frame, 0, 255).astype(np.uint16)
    frame = (frame * vig_mask()[:, :, None]) >> 8
    return np.clip(frame, 0, 255).astype(np.uint8)


def main():
    rng = np.random.default_rng(11)
    enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "22",
           "-pix_fmt", "yuv420p", "-g", "60", "-movflags", "+faststart"]
    proc = __import__("subprocess").Popen(
        [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-"] + enc + [OUT],
        stdin=__import__("subprocess").PIPE, stdout=__import__("subprocess").DEVNULL,
        stderr=__import__("subprocess").DEVNULL)

    starts, acc = [], 0
    for s in SEGS:
        starts.append(acc)
        acc += s[1]

    def frame_at(seg_i, local_i, t_global):
        return render_seg(seg_i, local_i / FPS, t_global, rng)

    for f in range(TOTAL):
        seg_i = max(i for i, st in enumerate(starts) if st <= f)
        local = f - starts[seg_i]
        t_global = f / FPS
        fr = frame_at(seg_i, local, t_global)

        # محو متقابل با نمای بعدی
        if seg_i + 1 < len(SEGS):
            nxt_start = starts[seg_i + 1]
            if f >= nxt_start - XFADE:
                a = (f - (nxt_start - XFADE) + 1) / (XFADE + 1)
                nxt = frame_at(seg_i + 1, f - nxt_start, t_global)
                fr = (fr.astype(np.float32) * (1 - a) + nxt.astype(np.float32) * a).astype(np.uint8)

        # محو ابتدا و انتها
        if f < 8:
            fr = (fr * (f / 8.0)).astype(np.uint8)
        if f > TOTAL - 16:
            fr = (fr * ((TOTAL - f) / 16.0)).astype(np.uint8)

        proc.stdin.write(fr.tobytes())
        if f % 60 == 0:
            print("frame", f, "/", TOTAL, flush=True)
    proc.stdin.close()
    proc.wait()
    print("DONE", OUT, round(os.path.getsize(OUT) / 1048576, 2), "MB")


if __name__ == "__main__":
    main()
