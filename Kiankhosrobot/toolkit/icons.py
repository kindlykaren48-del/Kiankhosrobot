import math
from PIL import Image, ImageDraw


def icon(kind, size=56, col=(25, 20, 50)):
    S = size * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(6, S // 14)
    c = S // 2

    def L(p, ww=None):
        d.line(p, fill=col, width=ww or w, joint="curve")

    if kind == "dna":
        for k in range(2):
            pts = []
            for i in range(41):
                t = i / 40
                pts.append((c + (S*0.24)*math.sin(t*6.28*1.5 + k*3.14159), S*0.12 + t*S*0.76))
            L(pts)
    elif kind == "ear":
        d.arc([S*0.24, S*0.12, S*0.78, S*0.80], 200, 110, fill=col, width=w)
        d.arc([S*0.40, S*0.30, S*0.66, S*0.60], 200, 110, fill=col, width=w)
    elif kind == "chart":
        L([(S*0.16, S*0.16), (S*0.16, S*0.84), (S*0.86, S*0.84)])
        for i, h in enumerate([0.30, 0.48, 0.22]):
            x = S*0.30 + i*S*0.20
            d.rounded_rectangle([x, S*0.84 - S*h, x + S*0.13, S*0.84], S*0.03, fill=col)
    elif kind == "face":
        d.ellipse([S*0.14, S*0.14, S*0.86, S*0.86], outline=col, width=w)
        d.ellipse([S*0.32, S*0.38, S*0.42, S*0.48], fill=col)
        d.ellipse([S*0.60, S*0.36, S*0.68, S*0.44], fill=col)
        d.arc([S*0.32, S*0.52, S*0.72, S*0.76], 10, 150, fill=col, width=w)
    elif kind == "sound":
        d.polygon([(S*0.16,S*0.38),(S*0.32,S*0.38),(S*0.50,S*0.20),(S*0.50,S*0.80),(S*0.32,S*0.62),(S*0.16,S*0.62)], fill=col)
        for r in [0.14, 0.26]:
            d.arc([S*0.50, S*0.50-S*r, S*0.50+2*S*r, S*0.50+S*r], 300, 60, fill=col, width=w)
    elif kind == "eye":
        d.chord([S*0.08,S*0.26,S*0.92,S*0.74], 180, 360, outline=col, width=w)
        d.chord([S*0.08,S*0.26,S*0.92,S*0.74], 0, 180, outline=col, width=w)
        d.ellipse([S*0.40,S*0.40,S*0.60,S*0.60], fill=col)
    elif kind == "stetho":
        d.arc([S*0.18,S*0.12,S*0.72,S*0.66], 180, 20, fill=col, width=w)
        L([(S*0.20,S*0.40),(S*0.20,S*0.52)]); L([(S*0.70,S*0.40),(S*0.70,S*0.52)])
        d.ellipse([S*0.10,S*0.52,S*0.30,S*0.72], outline=col, width=w)
        d.ellipse([S*0.60,S*0.52,S*0.80,S*0.72], outline=col, width=w)
        d.ellipse([S*0.42,S*0.66,S*0.72,S*0.94], outline=col, width=w)
    elif kind == "headphone":
        d.arc([S*0.14,S*0.16,S*0.86,S*0.80], 180, 0, fill=col, width=w)
        d.rounded_rectangle([S*0.10,S*0.48,S*0.30,S*0.84], S*0.07, fill=col)
        d.rounded_rectangle([S*0.70,S*0.48,S*0.90,S*0.84], S*0.07, fill=col)
    elif kind == "scan":
        d.rounded_rectangle([S*0.12,S*0.18,S*0.88,S*0.72], S*0.06, outline=col, width=w)
        d.ellipse([S*0.36,S*0.32,S*0.64,S*0.60], outline=col, width=w)
        L([(S*0.40,S*0.84),(S*0.60,S*0.84)]); L([(S*0.50,S*0.72),(S*0.50,S*0.84)])
    elif kind in ("heart", "heart2"):
        d.pieslice([S*0.10,S*0.20,S*0.52,S*0.62], 180, 360, fill=col)
        d.pieslice([S*0.48,S*0.20,S*0.90,S*0.62], 180, 360, fill=col)
        d.polygon([(S*0.11,S*0.42),(S*0.89,S*0.42),(S*0.50,S*0.88)], fill=col)
    elif kind == "aid":
        d.arc([S*0.26,S*0.14,S*0.76,S*0.72], 210, 120, fill=col, width=w)
        d.ellipse([S*0.56,S*0.58,S*0.84,S*0.86], fill=col)
        d.arc([S*0.14,S*0.30,S*0.44,S*0.60], 300, 60, fill=col, width=w)
    elif kind == "hospital":
        d.rounded_rectangle([S*0.16,S*0.30,S*0.84,S*0.86], S*0.05, outline=col, width=w)
        L([(S*0.50,S*0.40),(S*0.50,S*0.66)]); L([(S*0.37,S*0.53),(S*0.63,S*0.53)])
        d.polygon([(S*0.10,S*0.32),(S*0.50,S*0.10),(S*0.90,S*0.32)], fill=col)
    elif kind == "speak":
        d.rounded_rectangle([S*0.10,S*0.18,S*0.90,S*0.66], S*0.12, outline=col, width=w)
        d.polygon([(S*0.28,S*0.62),(S*0.46,S*0.62),(S*0.26,S*0.88)], fill=col)
    elif kind == "filter":
        d.polygon([(S*0.12,S*0.16),(S*0.88,S*0.16),(S*0.58,S*0.54),(S*0.58,S*0.86),(S*0.42,S*0.78),(S*0.42,S*0.54)], outline=col, width=w)
    elif kind == "kidney":
        d.ellipse([S*0.20,S*0.14,S*0.84,S*0.86], outline=col, width=w)
        L([(S*0.34,S*0.50),(S*0.20,S*0.50)])
    elif kind == "drop":
        d.polygon([(S*0.50,S*0.10),(S*0.82,S*0.56),(S*0.50,S*0.90),(S*0.18,S*0.56)], fill=col)
    elif kind == "battery":
        d.rounded_rectangle([S*0.10,S*0.32,S*0.80,S*0.68], S*0.06, outline=col, width=w)
        d.rounded_rectangle([S*0.82,S*0.42,S*0.92,S*0.58], S*0.03, fill=col)
        d.rectangle([S*0.18,S*0.40,S*0.36,S*0.60], fill=col)
    elif kind == "scale":
        d.rounded_rectangle([S*0.10,S*0.30,S*0.90,S*0.82], S*0.08, outline=col, width=w)
        d.arc([S*0.28,S*0.42,S*0.72,S*0.86], 200, 340, fill=col, width=w)
    elif kind == "strip":
        d.rounded_rectangle([S*0.36,S*0.08,S*0.64,S*0.92], S*0.05, outline=col, width=w)
        for i in range(4):
            y = S*(0.18 + i*0.17)
            d.rectangle([S*0.40, y, S*0.60, y+S*0.10], fill=col)
    elif kind == "lab":
        d.polygon([(S*0.36,S*0.10),(S*0.64,S*0.10),(S*0.64,S*0.42),(S*0.84,S*0.86),(S*0.16,S*0.86),(S*0.36,S*0.42)], outline=col, width=w)
        d.polygon([(S*0.30,S*0.62),(S*0.70,S*0.62),(S*0.84,S*0.86),(S*0.16,S*0.86)], fill=col)
    elif kind == "blood":
        d.rounded_rectangle([S*0.34,S*0.08,S*0.66,S*0.92], S*0.14, outline=col, width=w)
        d.rounded_rectangle([S*0.38,S*0.52,S*0.62,S*0.88], S*0.10, fill=col)
        L([(S*0.28,S*0.12),(S*0.72,S*0.12)])
    elif kind == "bp":
        d.rounded_rectangle([S*0.10,S*0.24,S*0.66,S*0.72], S*0.08, outline=col, width=w)
        d.ellipse([S*0.62,S*0.60,S*0.90,S*0.88], outline=col, width=w)
        L([(S*0.20,S*0.48),(S*0.30,S*0.48),(S*0.36,S*0.34),(S*0.44,S*0.62),(S*0.50,S*0.48),(S*0.58,S*0.48)], w//2)
    elif kind == "pill":
        d.rounded_rectangle([S*0.10,S*0.36,S*0.90,S*0.64], S*0.14, outline=col, width=w)
        L([(S*0.50,S*0.36),(S*0.50,S*0.64)])
        d.ellipse([S*0.16,S*0.42,S*0.28,S*0.54], fill=col)
    elif kind == "salt":
        d.polygon([(S*0.30,S*0.32),(S*0.70,S*0.32),(S*0.78,S*0.88),(S*0.22,S*0.88)], outline=col, width=w)
        d.arc([S*0.30,S*0.16,S*0.70,S*0.48], 180, 0, fill=col, width=w)
        L([(S*0.12,S*0.12),(S*0.88,S*0.92)], w)
    elif kind == "mosquito":
        d.ellipse([S*0.40,S*0.44,S*0.62,S*0.62], fill=col)
        d.ellipse([S*0.58,S*0.36,S*0.72,S*0.50], fill=col)
        d.ellipse([S*0.12,S*0.18,S*0.46,S*0.42], outline=col, width=w//2)
    elif kind == "worm":
        pts = [(S*0.10 + (i/40)*S*0.80, S*0.50 + S*0.22*math.sin((i/40)*6.28*1.6)) for i in range(41)]
        L(pts)
        d.ellipse([S*0.82,S*0.40,S*0.94,S*0.52], fill=col)
    elif kind == "leg":
        d.rounded_rectangle([S*0.36,S*0.10,S*0.58,S*0.46], S*0.08, fill=col)
        d.ellipse([S*0.22,S*0.40,S*0.76,S*0.80], fill=col)
        d.rounded_rectangle([S*0.20,S*0.74,S*0.84,S*0.90], S*0.07, fill=col)
    elif kind == "fever":
        d.rounded_rectangle([S*0.42,S*0.08,S*0.58,S*0.66], S*0.08, outline=col, width=w)
        d.ellipse([S*0.36,S*0.62,S*0.64,S*0.90], fill=col)
        d.rounded_rectangle([S*0.46,S*0.30,S*0.54,S*0.70], S*0.04, fill=col)
    elif kind == "skin":
        d.rounded_rectangle([S*0.12,S*0.24,S*0.88,S*0.78], S*0.08, outline=col, width=w)
        for i in range(3):
            y = S*(0.38 + i*0.16)
            L([(S*0.20,y),(S*0.80,y)], w//2)
    elif kind == "micro":
        d.ellipse([S*0.14,S*0.14,S*0.70,S*0.70], outline=col, width=w)
        L([(S*0.62,S*0.62),(S*0.88,S*0.88)], w+2)
        d.ellipse([S*0.30,S*0.34,S*0.40,S*0.44], fill=col)
    elif kind == "moon":
        d.pieslice([S*0.14,S*0.14,S*0.86,S*0.86], 0, 360, fill=col)
        d.pieslice([S*0.02,S*0.06,S*0.72,S*0.78], 0, 360, fill=(0,0,0,0))
    elif kind == "wash":
        d.arc([S*0.10,S*0.34,S*0.90,S*0.92], 0, 180, fill=col, width=w)
        L([(S*0.08,S*0.40),(S*0.92,S*0.40)])
        d.ellipse([S*0.40,S*0.10,S*0.62,S*0.30], outline=col, width=w)
    elif kind == "net":
        d.polygon([(S*0.50,S*0.08),(S*0.90,S*0.86),(S*0.10,S*0.86)], outline=col, width=w)
        for i in range(1, 4):
            y = S*(0.08 + i*0.195)
            dx = (y - S*0.08)/(S*0.78) * S*0.40
            L([(S*0.50-dx, y),(S*0.50+dx, y)], w//2)
    elif kind == "plant":
        L([(S*0.50,S*0.86),(S*0.50,S*0.42)])
        d.ellipse([S*0.14,S*0.30,S*0.50,S*0.54], fill=col)
        d.ellipse([S*0.50,S*0.22,S*0.86,S*0.46], fill=col)
    elif kind == "root":
        L([(S*0.50,S*0.10),(S*0.50,S*0.52)])
        d.ellipse([S*0.28,S*0.14,S*0.50,S*0.34], fill=col)
        for a in [(0.22,0.90),(0.50,0.94),(0.78,0.88)]:
            L([(S*0.50,S*0.52),(S*a[0],S*a[1])], w//2)
    elif kind == "globe":
        d.ellipse([S*0.12,S*0.12,S*0.88,S*0.88], outline=col, width=w)
        d.ellipse([S*0.36,S*0.12,S*0.64,S*0.88], outline=col, width=w//2)
        L([(S*0.14,S*0.50),(S*0.86,S*0.50)], w//2)
    elif kind == "lung":
        L([(S*0.50,S*0.10),(S*0.50,S*0.40)])
        d.pieslice([S*0.06,S*0.28,S*0.50,S*0.90], 90, 240, fill=col)
        d.pieslice([S*0.50,S*0.28,S*0.94,S*0.90], 300, 90, fill=col)
    elif kind == "virus":
        d.ellipse([S*0.28,S*0.28,S*0.72,S*0.72], fill=col)
        for i in range(8):
            a = i*math.pi/4
            x1, y1 = c + S*0.24*math.cos(a), c + S*0.24*math.sin(a)
            x2, y2 = c + S*0.42*math.cos(a), c + S*0.42*math.sin(a)
            L([(x1,y1),(x2,y2)], w//2)
            d.ellipse([x2-S*0.05, y2-S*0.05, x2+S*0.05, y2+S*0.05], fill=col)
    elif kind == "shield":
        d.polygon([(S*0.50,S*0.08),(S*0.88,S*0.24),(S*0.88,S*0.54),(S*0.50,S*0.92),(S*0.12,S*0.54),(S*0.12,S*0.24)], outline=col, width=w)
        L([(S*0.34,S*0.48),(S*0.46,S*0.62),(S*0.68,S*0.36)])
    elif kind == "nose":
        d.arc([S*0.24,S*0.10,S*0.86,S*0.72], 120, 290, fill=col, width=w)
        d.arc([S*0.34,S*0.54,S*0.62,S*0.82], 180, 360, fill=col, width=w)
    elif kind == "dropper":
        d.rounded_rectangle([S*0.38,S*0.06,S*0.62,S*0.22], S*0.05, fill=col)
        d.rounded_rectangle([S*0.42,S*0.22,S*0.58,S*0.62], S*0.03, outline=col, width=w)
        d.polygon([(S*0.42,S*0.62),(S*0.58,S*0.62),(S*0.50,S*0.78)], fill=col)
        d.ellipse([S*0.44,S*0.82,S*0.56,S*0.94], fill=col)
    elif kind in ("syrup", "vial"):
        d.rounded_rectangle([S*0.34,S*0.06,S*0.66,S*0.18], S*0.03, fill=col)
        d.rounded_rectangle([S*0.28,S*0.18,S*0.72,S*0.92], S*0.09, outline=col, width=w)
        d.rounded_rectangle([S*0.34,S*0.52,S*0.66,S*0.86], S*0.05, fill=col)
    elif kind in ("clock", "clockwait"):
        d.ellipse([S*0.10,S*0.10,S*0.90,S*0.90], outline=col, width=w)
        L([(S*0.50,S*0.50),(S*0.50,S*0.26)]); L([(S*0.50,S*0.50),(S*0.70,S*0.58)])
        d.ellipse([S*0.46,S*0.46,S*0.54,S*0.54], fill=col)
    elif kind == "calendar":
        d.rounded_rectangle([S*0.10,S*0.20,S*0.90,S*0.88], S*0.07, outline=col, width=w)
        L([(S*0.10,S*0.40),(S*0.90,S*0.40)])
        L([(S*0.30,S*0.08),(S*0.30,S*0.26)]); L([(S*0.70,S*0.08),(S*0.70,S*0.26)])
        for i in range(3):
            for j in range(2):
                x, y = S*(0.22+i*0.24), S*(0.52+j*0.18)
                d.rectangle([x, y, x+S*0.10, y+S*0.08], fill=col)
    elif kind == "pregnant":
        d.ellipse([S*0.38,S*0.06,S*0.62,S*0.30], fill=col)
        d.arc([S*0.28,S*0.30,S*0.56,S*0.94], 90, 270, fill=col, width=w)
        d.ellipse([S*0.46,S*0.40,S*0.84,S*0.78], outline=col, width=w)
    elif kind == "liver":
        d.pieslice([S*0.06,S*0.26,S*0.94,S*0.84], 180, 360, fill=col)
        d.polygon([(S*0.07,S*0.55),(S*0.93,S*0.55),(S*0.60,S*0.86),(S*0.30,S*0.80)], fill=col)
    elif kind == "warn":
        d.polygon([(S*0.50,S*0.08),(S*0.94,S*0.86),(S*0.06,S*0.86)], outline=col, width=w)
        L([(S*0.50,S*0.36),(S*0.50,S*0.62)])
        d.ellipse([S*0.44,S*0.70,S*0.56,S*0.82], fill=col)
    elif kind == "doctor":
        d.ellipse([S*0.34,S*0.08,S*0.66,S*0.40], outline=col, width=w)
        d.arc([S*0.12,S*0.44,S*0.88,S*1.10], 180, 360, fill=col, width=w)
        L([(S*0.50,S*0.52),(S*0.50,S*0.74)], w//2)
    elif kind == "valve":
        d.ellipse([S*0.12,S*0.12,S*0.88,S*0.88], outline=col, width=w)
        L([(S*0.30,S*0.62),(S*0.50,S*0.44),(S*0.70,S*0.62)])
    elif kind == "ecg":
        L([(S*0.06,S*0.50),(S*0.28,S*0.50),(S*0.36,S*0.22),(S*0.48,S*0.78),(S*0.58,S*0.50),(S*0.94,S*0.50)])
    elif kind == "dizzy":
        d.ellipse([S*0.20,S*0.16,S*0.80,S*0.76], outline=col, width=w)
        for dx in [0.32, 0.56]:
            L([(S*dx,S*0.38),(S*dx+S*0.12,S*0.50)], w//2)
            L([(S*dx+S*0.12,S*0.38),(S*dx,S*0.50)], w//2)
    elif kind == "chest":
        d.rounded_rectangle([S*0.16,S*0.20,S*0.84,S*0.86], S*0.14, outline=col, width=w)
        d.pieslice([S*0.30,S*0.36,S*0.52,S*0.58], 180, 360, fill=col)
        d.pieslice([S*0.48,S*0.36,S*0.70,S*0.58], 180, 360, fill=col)
        d.polygon([(S*0.31,S*0.47),(S*0.69,S*0.47),(S*0.50,S*0.72)], fill=col)
    elif kind == "probe":
        d.rounded_rectangle([S*0.38,S*0.06,S*0.62,S*0.46], S*0.08, fill=col)
        d.polygon([(S*0.34,S*0.50),(S*0.66,S*0.50),(S*0.86,S*0.92),(S*0.14,S*0.92)], outline=col, width=w)
    elif kind == "surgery":
        L([(S*0.14,S*0.86),(S*0.72,S*0.28)])
        d.polygon([(S*0.66,S*0.22),(S*0.90,S*0.10),(S*0.78,S*0.34)], fill=col)
    elif kind == "run":
        d.ellipse([S*0.54,S*0.08,S*0.74,S*0.28], fill=col)
        L([(S*0.30,S*0.46),(S*0.56,S*0.36),(S*0.76,S*0.46)])
        L([(S*0.56,S*0.36),(S*0.50,S*0.62)])
        L([(S*0.50,S*0.62),(S*0.30,S*0.86)]); L([(S*0.50,S*0.62),(S*0.72,S*0.80)])
    elif kind == "babyhead":
        d.ellipse([S*0.16,S*0.14,S*0.84,S*0.82], outline=col, width=w)
        d.ellipse([S*0.36,S*0.40,S*0.44,S*0.48], fill=col)
        d.ellipse([S*0.58,S*0.40,S*0.66,S*0.48], fill=col)
        d.arc([S*0.38,S*0.52,S*0.64,S*0.70], 10, 170, fill=col, width=w//2)
        d.arc([S*0.44,S*0.06,S*0.66,S*0.24], 150, 340, fill=col, width=w//2)
    elif kind == "flake":
        for (x, y, r) in [(0.30,0.30,0.13),(0.62,0.26,0.10),(0.44,0.56,0.15),(0.72,0.60,0.11),(0.28,0.74,0.09)]:
            d.ellipse([S*(x-r),S*(y-r),S*(x+r),S*(y+r)], outline=col, width=w//2)
    elif kind == "oilgland":
        L([(S*0.20,S*0.24),(S*0.86,S*0.24)])
        d.ellipse([S*0.34,S*0.40,S*0.66,S*0.72], outline=col, width=w)
        d.polygon([(S*0.50,S*0.78),(S*0.60,S*0.90),(S*0.40,S*0.90)], fill=col)
    elif kind == "noitch":
        d.ellipse([S*0.20,S*0.20,S*0.80,S*0.80], outline=col, width=w)
        L([(S*0.32,S*0.32),(S*0.68,S*0.68)])
    elif kind == "safe":
        d.polygon([(S*0.50,S*0.08),(S*0.88,S*0.24),(S*0.88,S*0.54),(S*0.50,S*0.92),(S*0.12,S*0.54),(S*0.12,S*0.24)], outline=col, width=w)
        d.pieslice([S*0.28,S*0.34,S*0.52,S*0.58], 180, 360, fill=col)
        d.pieslice([S*0.48,S*0.34,S*0.72,S*0.58], 180, 360, fill=col)
        d.polygon([(S*0.29,S*0.46),(S*0.71,S*0.46),(S*0.50,S*0.70)], fill=col)
    elif kind == "brush":
        d.rounded_rectangle([S*0.20,S*0.16,S*0.80,S*0.46], S*0.14, outline=col, width=w)
        for i in range(5):
            x = S*(0.28 + i*0.12)
            L([(x,S*0.46),(x,S*0.66)], w//2)
        d.rounded_rectangle([S*0.42,S*0.66,S*0.58,S*0.92], S*0.06, fill=col)
    elif kind == "oil":
        d.rounded_rectangle([S*0.40,S*0.06,S*0.60,S*0.20], S*0.04, fill=col)
        d.rounded_rectangle([S*0.28,S*0.20,S*0.72,S*0.74], S*0.10, outline=col, width=w)
        d.polygon([(S*0.50,S*0.78),(S*0.62,S*0.92),(S*0.38,S*0.92)], fill=col)
    elif kind == "shampoo":
        d.rounded_rectangle([S*0.42,S*0.04,S*0.58,S*0.18], S*0.03, fill=col)
        d.rounded_rectangle([S*0.28,S*0.18,S*0.72,S*0.90], S*0.10, outline=col, width=w)
        d.rounded_rectangle([S*0.34,S*0.50,S*0.66,S*0.84], S*0.06, fill=col)
    elif kind == "nohand":
        d.rounded_rectangle([S*0.32,S*0.34,S*0.68,S*0.86], S*0.10, outline=col, width=w)
        for i in range(3):
            x = S*(0.36 + i*0.12)
            L([(x,S*0.34),(x,S*0.16)], w//2)
        L([(S*0.10,S*0.12),(S*0.90,S*0.92)], w+2)
    elif kind == "spider":
        d.ellipse([S*0.36,S*0.34,S*0.64,S*0.56], fill=col)
        d.ellipse([S*0.32,S*0.52,S*0.68,S*0.84], fill=col)
        for sgn in (-1, 1):
            for (y0, y1) in [(0.42,0.22),(0.50,0.36),(0.58,0.54),(0.66,0.74)]:
                d.line([(c+sgn*S*0.14, S*y0), (c+sgn*S*0.32, S*((y0+y1)/2)), (c+sgn*S*0.46, S*y1)],
                       fill=col, width=max(4, w//2), joint="curve")
    elif kind == "hourglass":
        d.polygon([(S*0.30,S*0.16),(S*0.70,S*0.16),(S*0.50,S*0.50)], fill=col)
        d.polygon([(S*0.50,S*0.50),(S*0.70,S*0.84),(S*0.30,S*0.84)], fill=col)
    elif kind == "web":
        for i in range(6):
            a = i*math.pi/3
            L([(c,c),(c+S*0.44*math.cos(a), c+S*0.44*math.sin(a))], w//2)
        for r in (0.16, 0.28, 0.40):
            pts = [(c+S*r*math.cos(i*math.pi/3), c+S*r*math.sin(i*math.pi/3)) for i in range(7)]
            d.line(pts, fill=col, width=max(3, w//2), joint="curve")
    elif kind == "bite":
        d.ellipse([S*0.14,S*0.20,S*0.86,S*0.84], outline=col, width=w)
        d.ellipse([S*0.38,S*0.42,S*0.48,S*0.52], fill=col)
        d.ellipse([S*0.54,S*0.42,S*0.64,S*0.52], fill=col)
    elif kind == "cramp":
        d.arc([S*0.18,S*0.18,S*0.82,S*0.82], 40, 320, fill=col, width=w)
        L([(S*0.34,S*0.40),(S*0.48,S*0.54),(S*0.36,S*0.66)], w//2)
    elif kind == "sweat":
        d.arc([S*0.16,S*0.14,S*0.84,S*0.72], 180, 360, fill=col, width=w)
        for x in (0.28, 0.50, 0.72):
            d.polygon([(S*x,S*0.62),(S*(x+0.07),S*0.80),(S*(x-0.07),S*0.80)], fill=col)
    elif kind == "ice":
        d.rounded_rectangle([S*0.18,S*0.18,S*0.82,S*0.82], S*0.10, outline=col, width=w)
        L([(S*0.50,S*0.26),(S*0.50,S*0.74)], w//2); L([(S*0.26,S*0.50),(S*0.74,S*0.50)], w//2)
        L([(S*0.33,S*0.33),(S*0.67,S*0.67)], w//2); L([(S*0.67,S*0.33),(S*0.33,S*0.67)], w//2)
    elif kind == "ambulance":
        d.rounded_rectangle([S*0.08,S*0.34,S*0.66,S*0.70], S*0.06, outline=col, width=w)
        d.polygon([(S*0.66,S*0.44),(S*0.84,S*0.44),(S*0.92,S*0.58),(S*0.92,S*0.70),(S*0.66,S*0.70)], outline=col, width=w)
        d.ellipse([S*0.20,S*0.68,S*0.36,S*0.84], fill=col)
        d.ellipse([S*0.66,S*0.68,S*0.82,S*0.84], fill=col)
    elif kind == "thermo":
        d.rounded_rectangle([S*0.40,S*0.10,S*0.60,S*0.66], S*0.10, outline=col, width=w)
        d.ellipse([S*0.33,S*0.62,S*0.67,S*0.96], outline=col, width=w)
        d.ellipse([S*0.41,S*0.70,S*0.59,S*0.88], fill=col)
        for i in range(3):
            L([(S*0.64,S*0.22+i*S*0.14),(S*0.78,S*0.22+i*S*0.14)], w//2)
    elif kind == "cut":
        d.ellipse([S*0.10,S*0.62,S*0.34,S*0.86], outline=col, width=w)
        d.ellipse([S*0.66,S*0.62,S*0.90,S*0.86], outline=col, width=w)
        L([(S*0.30,S*0.66),(S*0.80,S*0.14)]); L([(S*0.70,S*0.66),(S*0.20,S*0.14)])
    elif kind == "meat":
        d.ellipse([S*0.12,S*0.20,S*0.84,S*0.80], outline=col, width=w)
        d.ellipse([S*0.30,S*0.36,S*0.62,S*0.64], fill=col)
        d.ellipse([S*0.66,S*0.62,S*0.92,S*0.88], outline=col, width=w)
    elif kind == "chicken":
        d.ellipse([S*0.18,S*0.14,S*0.72,S*0.62], outline=col, width=w)
        L([(S*0.60,S*0.54),(S*0.86,S*0.86)])
        d.ellipse([S*0.76,S*0.76,S*0.96,S*0.96], outline=col, width=w)
    elif kind == "fish":
        d.ellipse([S*0.10,S*0.30,S*0.72,S*0.70], outline=col, width=w)
        d.polygon([(S*0.70,S*0.50),(S*0.94,S*0.26),(S*0.94,S*0.74)], outline=col, width=w)
        d.ellipse([S*0.22,S*0.44,S*0.32,S*0.54], fill=col)
    elif kind == "plate":
        d.ellipse([S*0.10,S*0.24,S*0.90,S*0.80], outline=col, width=w)
        d.ellipse([S*0.24,S*0.36,S*0.76,S*0.68], outline=col, width=w//2)
        L([(S*0.50,S*0.80),(S*0.50,S*0.92)])
    elif kind == "fridge":
        d.rounded_rectangle([S*0.24,S*0.06,S*0.76,S*0.94], S*0.08, outline=col, width=w)
        L([(S*0.24,S*0.40),(S*0.76,S*0.40)])
        L([(S*0.64,S*0.18),(S*0.64,S*0.32)], w//2)
        L([(S*0.64,S*0.50),(S*0.64,S*0.64)], w//2)
    elif kind == "no":
        d.ellipse([S*0.12,S*0.12,S*0.88,S*0.88], outline=col, width=w)
        L([(S*0.28,S*0.28),(S*0.72,S*0.72)])
    elif kind == "repeat":
        d.arc([S*0.14,S*0.14,S*0.86,S*0.86], 40, 330, fill=col, width=w)
        d.polygon([(S*0.80,S*0.10),(S*0.96,S*0.30),(S*0.68,S*0.32)], fill=col)
    elif kind == "fire":
        d.polygon([(S*0.50,S*0.06),(S*0.80,S*0.44),(S*0.84,S*0.66),
                   (S*0.50,S*0.94),(S*0.16,S*0.66),(S*0.24,S*0.38)], outline=col, width=w)
        d.ellipse([S*0.38,S*0.58,S*0.62,S*0.86], fill=col)
    elif kind == "plus":
        d.ellipse([S*0.10,S*0.10,S*0.90,S*0.90], outline=col, width=w)
        L([(S*0.50,S*0.28),(S*0.50,S*0.72)]); L([(S*0.28,S*0.50),(S*0.72,S*0.50)])
    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi/2 + i*math.pi/5
            r = S*0.42 if i % 2 == 0 else S*0.18
            pts.append((c + r*math.cos(a), c + r*math.sin(a)))
        d.polygon(pts, fill=col)
    else:
        d.ellipse([S*0.24, S*0.24, S*0.76, S*0.76], fill=col)

    return im.resize((size, size), Image.LANCZOS)
