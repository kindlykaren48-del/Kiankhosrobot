"""Procedural flat-style illustrations (no external images, no API) for the reel engine.
Every scene is 1000x1250 (4:5). Drawn at 2x and downsampled for smooth edges."""
import math, random
from PIL import Image, ImageDraw, ImageFilter

S = 2                       # supersample factor
CW, CH = 1000, 1250

SKIN = (255, 214, 186); SKIN_D = (240, 176, 140); BLUSH = (255, 140, 150)
HAIR_B = (112, 66, 38); HAIR_M = (52, 32, 30); MOUTH = (205, 76, 86)
WHITE = (255, 255, 255)


def _canvas(c_top, c_bot):
    im = Image.new("RGB", (CW*S, CH*S))
    d = ImageDraw.Draw(im)
    for y in range(CH*S):
        f = y/(CH*S)
        d.line([(0, y), (CW*S, y)], fill=tuple(int(c_top[k]+(c_bot[k]-c_top[k])*f) for k in range(3)))
    return im


def _blobs(im, cols, seed=3, n=9, amax=70):
    r = random.Random(seed)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(n):
        c = cols[i % len(cols)]
        x, y, rad = r.randint(0, CW*S), r.randint(0, CH*S), r.randint(120, 330)*S
        od.ellipse([x-rad, y-rad, x+rad, y+rad], fill=c+(r.randint(30, amax),))
    ov = ov.filter(ImageFilter.GaussianBlur(60))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def _p(v):  # scale helper
    return int(round(v*S))


def ell(d, cx, cy, rx, ry, fill, ang=0, outline=None, w=0):
    pts = []
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for i in range(121):
        t = i/120*2*math.pi
        x, y = rx*math.cos(t), ry*math.sin(t)
        pts.append((_p(cx + x*ca - y*sa), _p(cy + x*sa + y*ca)))
    d.polygon(pts, fill=fill, outline=outline, width=w)


def circ(d, cx, cy, r, fill, outline=None, w=0):
    d.ellipse([_p(cx-r), _p(cy-r), _p(cx+r), _p(cy+r)], fill=fill, outline=outline, width=_p(w) if w else 0)


def heart(d, cx, cy, s, fill):
    pts = []
    for i in range(101):
        t = i/100*2*math.pi
        x = 16*math.sin(t)**3
        y = -(13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t))
        pts.append((_p(cx + x*s/16), _p(cy + y*s/16)))
    d.polygon(pts, fill=fill)


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(8):
        a = i*math.pi/4
        rr = r if i % 2 == 0 else r*0.28
        pts.append((_p(cx + rr*math.sin(a)), _p(cy - rr*math.cos(a))))
    d.polygon(pts, fill=fill)


def note(d, cx, cy, s, fill):
    circ(d, cx, cy, s*0.34, fill)
    d.rectangle([_p(cx+s*0.24), _p(cy-s*1.15), _p(cx+s*0.36), _p(cy)], fill=fill)
    d.polygon([(_p(cx+s*0.36), _p(cy-s*1.15)), (_p(cx+s*0.86), _p(cy-s*0.78)),
               (_p(cx+s*0.36), _p(cy-s*0.70))], fill=fill)


def waves(d, cx, cy, r0, n, step, a0, a1, col, w=14, alphas=None):
    for i in range(n):
        r = r0 + i*step
        d.arc([_p(cx-r), _p(cy-r), _p(cx+r), _p(cy+r)], a0, a1, fill=col, width=_p(w))


def baby_face(d, cx, cy, r, eyes="closed", look=0, hair=True, cap=None, cheek=True):
    # ears
    circ(d, cx-r*0.98, cy+r*0.05, r*0.17, SKIN_D); circ(d, cx+r*0.98, cy+r*0.05, r*0.17, SKIN_D)
    circ(d, cx, cy, r, SKIN)
    if cap:
        d.pieslice([_p(cx-r), _p(cy-r), _p(cx+r), _p(cy+r)], 180, 360, fill=cap)
        d.rectangle([_p(cx-r), _p(cy-r*0.04), _p(cx+r), _p(cy+r*0.06)], fill=tuple(max(0, c-25) for c in cap))
    elif hair:
        d.arc([_p(cx-r*0.28), _p(cy-r*1.28), _p(cx+r*0.28), _p(cy-r*0.84)], 190, 20, fill=HAIR_B, width=_p(r*0.07))
    ey = cy + r*0.08
    for sx in (-1, 1):
        ex = cx + sx*r*0.40
        if eyes == "closed":
            d.arc([_p(ex-r*0.17), _p(ey-r*0.10), _p(ex+r*0.17), _p(ey+r*0.16)], 10, 170, fill=(70, 45, 40), width=_p(r*0.055))
        else:
            circ(d, ex, ey, r*0.16, WHITE); circ(d, ex+look*r*0.07, ey, r*0.095, (60, 40, 40))
            circ(d, ex+look*r*0.07+r*0.03, ey-r*0.03, r*0.03, WHITE)
    if cheek:
        ell(d, cx-r*0.62, cy+r*0.40, r*0.17, r*0.11, BLUSH); ell(d, cx+r*0.62, cy+r*0.40, r*0.17, r*0.11, BLUSH)
    d.arc([_p(cx-r*0.17), _p(cy+r*0.28), _p(cx+r*0.17), _p(cy+r*0.58)], 20, 160, fill=MOUTH, width=_p(r*0.055))
    ell(d, cx, cy+r*0.22, r*0.05, r*0.04, SKIN_D)


def mom_face(d, cx, cy, r, hair=HAIR_M, mouth_open=True):
    ell(d, cx, cy+r*0.55, r*1.28, r*1.45, hair)                        # long hair back
    d.rectangle([_p(cx-r*0.28), _p(cy+r*0.7), _p(cx+r*0.28), _p(cy+r*1.35)], fill=SKIN_D)  # neck
    circ(d, cx-r*0.97, cy+r*0.06, r*0.13, SKIN_D); circ(d, cx+r*0.97, cy+r*0.06, r*0.13, SKIN_D)
    circ(d, cx, cy, r, SKIN)
    d.pieslice([_p(cx-r*1.04), _p(cy-r*1.06), _p(cx+r*1.04), _p(cy+r*0.9)], 180, 360, fill=hair)  # fringe
    ell(d, cx+r*0.16, cy+r*0.06, r*0.98, r*0.62, SKIN, ang=-8)
    for sx in (-1, 1):
        ex = cx + sx*r*0.38
        d.arc([_p(ex-r*0.15), _p(cy-r*0.02), _p(ex+r*0.15), _p(cy+r*0.22)], 190, 350, fill=(60, 40, 36), width=_p(r*0.05))
        circ(d, ex, cy+r*0.10, r*0.06, (60, 40, 36))
    ell(d, cx-r*0.58, cy+r*0.42, r*0.15, r*0.10, BLUSH); ell(d, cx+r*0.58, cy+r*0.42, r*0.15, r*0.10, BLUSH)
    if mouth_open:
        ell(d, cx, cy+r*0.48, r*0.17, r*0.13, MOUTH); ell(d, cx, cy+r*0.54, r*0.10, r*0.05, (240, 130, 130))
    else:
        d.arc([_p(cx-r*0.2), _p(cy+r*0.28), _p(cx+r*0.2), _p(cy+r*0.6)], 20, 160, fill=MOUTH, width=_p(r*0.05))


def _finish(im):
    return im.resize((CW, CH), Image.LANCZOS)


# ------------------------------------------------------------------ scenes
def scene_womb(variant="slide"):
    """Baby curled in the womb, mother's voice waves arriving."""
    im = _canvas((255, 226, 214), (255, 190, 176)) if variant == "slide" else _canvas((255, 214, 220), (186, 214, 255))
    im = _blobs(im, [(255, 255, 255), (255, 150, 170), (150, 200, 255)], seed=5)
    d = ImageDraw.Draw(im, "RGBA")
    # belly
    circ(d, 700, 720, 520, SKIN)
    circ(d, 700, 720, 520, None, outline=(236, 160, 128), w=10)
    # amniotic sac
    circ(d, 640, 700, 330, (190, 226, 255)); circ(d, 640, 700, 330, None, outline=(120, 176, 240), w=12)
    circ(d, 640, 700, 285, (214, 238, 255))
    # baby body curled
    ell(d, 660, 790, 150, 105, (255, 205, 175), ang=-20)
    ell(d, 745, 850, 70, 40, SKIN_D, ang=-30)           # feet
    ell(d, 560, 800, 52, 34, SKIN_D, ang=20)             # hand
    baby_face(d, 600, 660, 110, eyes="closed")
    # umbilical cord curl
    d.arc([_p(660), _p(840), _p(800), _p(960)], 180, 40, fill=(255, 160, 160), width=_p(14))
    # sound waves from the left (mother's voice)
    for i, rr in enumerate((110, 190, 270)):
        d.arc([_p(130-rr), _p(520-rr), _p(130+rr), _p(520+rr)], -48, 48, fill=(255, 255, 255, 235 - i*50), width=_p(18))
    circ(d, 130, 520, 38, (255, 255, 255, 240)); heart(d, 130, 524, 42, (255, 80, 110))
    note(d, 160, 250, 52, (255, 255, 255)); note(d, 330, 170, 40, (255, 255, 255, 220))
    star(d, 860, 240, 34, (255, 255, 255, 230)); star(d, 130, 1000, 26, (255, 255, 255, 200)); star(d, 900, 1120, 30, (255, 255, 255, 220))
    return _finish(im)


def scene_prefers_mom():
    im = _canvas((200, 230, 255), (190, 245, 220))
    im = _blobs(im, [(255, 255, 255), (130, 190, 255), (150, 240, 180)], seed=8)
    d = ImageDraw.Draw(im, "RGBA")
    mom_face(d, 330, 360, 190)
    for i, rr in enumerate((120, 200, 280)):
        d.arc([_p(560-rr+30), _p(470-rr), _p(560+rr+30), _p(470+rr)], -40, 40, fill=(255, 255, 255, 235-i*45), width=_p(18))
    note(d, 700, 300, 54, (255, 120, 150)); note(d, 830, 410, 44, (90, 140, 255))
    # baby with blanket
    ell(d, 640, 1130, 330, 150, (255, 190, 200))
    ell(d, 640, 1075, 300, 120, (255, 214, 224))
    baby_face(d, 640, 890, 170, eyes="open", look=-1, cap=(130, 190, 255))
    heart(d, 880, 800, 70, (255, 80, 110)); heart(d, 400, 820, 46, (255, 120, 150))
    star(d, 120, 760, 30, (255, 255, 255, 230)); star(d, 900, 1000, 26, (255, 255, 255, 220))
    return _finish(im)


def scene_notice():
    im = _canvas((214, 255, 232), (190, 225, 255))
    im = _blobs(im, [(255, 255, 255), (120, 230, 170), (130, 180, 255)], seed=11)
    d = ImageDraw.Draw(im, "RGBA")
    # soft crib/blanket
    ell(d, 500, 1120, 470, 190, (255, 255, 255, 235))
    ell(d, 500, 1090, 440, 150, (180, 220, 255))
    baby_face(d, 560, 700, 270, eyes="open", look=-1.6, cap=(120, 220, 170))
    # sound coming from the left
    for i, rr in enumerate((90, 170, 250)):
        d.arc([_p(110-rr), _p(660-rr), _p(110+rr), _p(660+rr)], -50, 50, fill=(60, 140, 255, 240-i*55), width=_p(20))
    circ(d, 110, 660, 46, (60, 140, 255)); 
    d.polygon([(_p(92), _p(640)), (_p(112), _p(640)), (_p(134), _p(620)), (_p(134), _p(700)), (_p(112), _p(680)), (_p(92), _p(680))], fill=WHITE)
    # calm "ok" badge
    circ(d, 860, 260, 92, (255, 255, 255, 240)); circ(d, 860, 260, 92, None, outline=(60, 190, 120), w=12)
    d.line([(_p(818), _p(262)), (_p(850), _p(298)), (_p(906), _p(228))], fill=(60, 190, 120), width=_p(20), joint="curve")
    heart(d, 820, 470, 48, (255, 100, 130)); star(d, 110, 220, 30, (255, 255, 255, 230)); star(d, 900, 1000, 26, (255, 255, 255, 220))
    return _finish(im)


def scene_lullaby():
    im = _canvas((60, 80, 170), (130, 90, 190))
    im = _blobs(im, [(120, 160, 255), (255, 170, 220), (255, 230, 150)], seed=14, amax=90)
    d = ImageDraw.Draw(im, "RGBA")
    # moon & stars
    circ(d, 780, 250, 130, (255, 236, 160)); circ(d, 830, 220, 112, (92, 92, 190))
    rr = random.Random(2)
    for _ in range(22):
        star(d, rr.randint(40, 960), rr.randint(40, 520), rr.randint(9, 22), (255, 255, 255, rr.randint(150, 240)))
    # mom + baby cuddle
    ell(d, 480, 1180, 560, 330, (255, 160, 190))                       # mom's body
    mom_face(d, 370, 640, 190, mouth_open=True)
    ell(d, 600, 960, 330, 230, (255, 214, 224), ang=-10)               # blanket bundle
    baby_face(d, 640, 840, 150, eyes="closed", cap=(255, 190, 120))
    ell(d, 520, 1010, 150, 70, SKIN, ang=-25)                          # mom's arm
    note(d, 160, 330, 62, (255, 236, 160)); note(d, 270, 190, 46, (255, 190, 220)); note(d, 560, 260, 40, (150, 210, 255))
    heart(d, 860, 820, 62, (255, 110, 150))
    return _finish(im)


def scene_cover():
    im = _canvas((120, 70, 190), (40, 130, 220))
    im = _blobs(im, [(255, 120, 170), (120, 255, 190), (255, 255, 255)], seed=21, amax=110)
    d = ImageDraw.Draw(im, "RGBA")
    # glowing sac
    for g, a in ((420, 40), (360, 70), (310, 110)):
        circ(d, 500, 640, g, (255, 255, 255, a))
    circ(d, 500, 640, 280, (200, 232, 255)); circ(d, 500, 640, 280, None, outline=(255, 255, 255), w=12)
    ell(d, 520, 735, 130, 92, (255, 205, 175), ang=-20)
    ell(d, 590, 790, 60, 36, SKIN_D, ang=-28)
    baby_face(d, 470, 600, 105, eyes="closed")
    # waves from both sides = parents' voices
    for side, cx0 in ((-1, 70), (1, 930)):
        for i, rr in enumerate((90, 170, 250)):
            a0, a1 = (-45, 45) if side == -1 else (135, 225)
            d.arc([_p(cx0-rr), _p(640-rr), _p(cx0+rr), _p(640+rr)], a0, a1, fill=(255, 255, 255, 235-i*50), width=_p(18))
    heart(d, 140, 1010, 90, (255, 100, 140)); heart(d, 860, 1030, 70, (120, 255, 190))
    note(d, 200, 260, 62, (255, 236, 160)); note(d, 800, 250, 52, (255, 236, 160))
    rr = random.Random(9)
    for _ in range(16):
        star(d, rr.randint(40, 960), rr.randint(60, 1180), rr.randint(10, 24), (255, 255, 255, rr.randint(150, 235)))
    return _finish(im)


def scene_generic(icon_name, idx=0):
    from icons import icon
    pals = [((200, 230, 255), (190, 245, 220)), ((255, 226, 214), (255, 200, 220)),
            ((214, 255, 232), (190, 225, 255)), ((226, 210, 255), (200, 220, 255))]
    top, bot = pals[idx % 4]
    im = _blobs(_canvas(top, bot), [(255, 255, 255), (120, 180, 255), (140, 235, 170), (255, 150, 170)], seed=30+idx)
    d = ImageDraw.Draw(im, "RGBA")
    for g, a in ((430, 40), (370, 70), (320, 110)):
        circ(d, 500, 620, g, (255, 255, 255, a))
    circ(d, 500, 620, 270, (255, 255, 255, 245)); circ(d, 500, 620, 270, None, outline=(90, 150, 240), w=14)
    ic = icon(icon_name, 330, (40, 90, 190)).resize((330*S, 330*S), Image.LANCZOS)
    im.paste(ic, (_p(500)-165*S, _p(620)-165*S), ic)
    rr = random.Random(idx)
    for _ in range(18):
        star(d, rr.randint(40, 960), rr.randint(60, 1190), rr.randint(10, 26), (255, 255, 255, rr.randint(150, 240)))
    heart(d, 160, 1040, 70, (255, 100, 140)); note(d, 860, 240, 50, (90, 140, 255))
    return _finish(im)


def bg_cover(path="bg_cover.png"):
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        f = y/H
        d.line([(0, y), (W, y)], fill=(int(30+20*f), int(40+90*f), int(120+90*f)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    r = random.Random(4)
    for i in range(14):
        c = [(120, 255, 170), (255, 110, 150), (140, 190, 255)][i % 3]
        x, y, rad = r.randint(0, W), r.randint(0, H), r.randint(120, 320)
        od.ellipse([x-rad, y-rad, x+rad, y+rad], fill=c+(r.randint(40, 90),))
    ov = ov.filter(ImageFilter.GaussianBlur(70))
    Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB").save(path)


def make_all(prefix="ill"):
    out = [f"{prefix}_cover.png"] + [f"{prefix}_{i}.png" for i in range(1, 5)]
    for p, fn in zip(out, (scene_cover, scene_womb, scene_prefers_mom, scene_notice, scene_lullaby)):
        fn().save(p)
    bg_cover()
    return out


if __name__ == "__main__":
    print(make_all())
