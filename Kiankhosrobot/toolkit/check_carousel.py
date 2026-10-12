"""
check_carousel.py — بررسی چیدمان کاروسل پیش از تحویل

هر متن و تصویری که روی اسلایدها رسم می‌شود را در یک اجرای خشک (بدون ذخیره)
ثبت می‌کند و گزارش می‌دهد که:
  · هیچ متنی از حاشیهٔ امن بیرون نزده باشد،
  · متن‌ها روی کارت تصویر نیفتاده باشند،
  · نکته‌ها در فضای اختصاصی‌شان جا شده باشند.

اجرا:  python3 check_carousel.py [slug]
"""
import sys

import make_carousel as mc
from make_carousel import W, H, PALETTES, F, BLACK, _font_info
from fatext import render_mask, _offsets

SAFE = (46, 46, W - 46, H - 36)
BOXES = []


class RecFD(mc.FD):
    def text(self, xy, text, font=None, fill=None, anchor=None, **kw):
        box = super().text(xy, text, font=font, fill=fill, anchor=anchor, **kw)
        BOXES[-1].append((str(text), tuple(box), "text"))
        return box


def rec_grad(img, xy, text, font, c1, c2, anchor="mm"):
    path, size = _font_info(font)
    mask, x0, y0, adv, asc, desc = render_mask(text, path, size)
    x1, y1 = x0 + mask.width, y0 + mask.height
    ox, base, box = _offsets(anchor, xy, (x0, y0, x1, y1), adv, asc, desc)
    BOXES[-1].append((str(text), tuple(box), "grad"))
    return _orig_grad(img, xy, text, font, c1, c2, anchor)


def rec_spaced(img, xy, text, font, fill, sp=6, anchor="ra"):
    d = mc.FD(img)
    total = sum(d.textlength(c, font=font) for c in text) + sp * max(0, len(text) - 1)
    x = xy[0] - total if anchor == "ra" else (xy[0] - total / 2 if anchor == "ma" else xy[0])
    BOXES[-1].append((str(text), (x, xy[1] - font.size, x + total, xy[1] + font.size * 0.3),
                      "spaced"))
    return _orig_spaced(img, xy, text, font, fill, sp, anchor)


def rec_card(src, cw, ch, pal, radius=44, crop=(0.04, 0.96), seed=1):
    im = _orig_card(src, cw, ch, pal, radius, crop, seed)
    BOXES[-1].append(("[card]", (0, 0, 0, 0), "card-begin"))
    return im


mc.FD = RecFD
_orig_grad, _orig_spaced = mc.grad_text, mc.spaced_text
mc.grad_text, mc.spaced_text = rec_grad, rec_spaced


def run(cfg):
    pal = PALETTES.get(cfg.get("palette", "rosegold"), PALETTES["rosegold"])
    total = len(cfg["slides"]) + 2
    jobs = [("کاور", lambda: mc.slide_cover(cfg, pal, 0, total))]
    for i in range(len(cfg["slides"])):
        jobs.append((f"اسلاید {i+1}", (lambda k: (lambda: mc.slide_content(cfg, pal, k, total)))(i)))
    jobs.append(("CTA", lambda: mc.slide_cta(cfg, pal, total)))

    bad = 0
    for name, fn in jobs:
        BOXES.append([])
        fn()
        boxes = [b for b in BOXES[-1] if b[2] != "card-begin"]
        out = [b for b in boxes if b[1][0] < SAFE[0] or b[1][1] < SAFE[1]
               or b[1][2] > SAFE[2] or b[1][3] > SAFE[3]]
        bot = max(b[1][3] for b in boxes)
        print(f"\n{name}: {len(boxes)} متن | پایین‌ترین لبهٔ متن y={bot}")
        for t, b, k in out:
            print("   ✘ بیرون از حاشیه:", t[:40], b)
            bad += 1
        if not out:
            print("   ✔ همهٔ متن‌ها در حاشیهٔ امن")
        if name.startswith("اسلاید"):
            sz, tot, avail = mc.LAST_BULLET
            print(f"   اندازهٔ نکته‌ها: {sz}px | ارتفاع مصرفی {tot} از {avail} مجاز")
            if tot > avail:
                print("   ✘ نکته‌ها از فضای خود بیرون زده‌اند")
                bad += 1
    print("\nجمع خطاها:", bad)
    return bad


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "newbornsmell"
    mod = __import__("topic_" + slug)
    sys.exit(1 if run(mod.cfg) else 0)
