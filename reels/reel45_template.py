#!/usr/bin/env python3
"""قالب ثابت و قفل‌شدهٔ کاروسل‌ها — سبک اسلایدهای ریل روی بوم ۴:۵ (۱۰۸۰×۱۳۵۰) 🔒

به درخواست دکتر کیانوش سالاریان، از کاروسل car05 به بعد همهٔ کاروسل‌ها
دقیقاً با همین قالب ساخته می‌شوند و نباید تغییر کند:

- گرادیان عمودی bg1→bg2 + هاله‌های سفید محو (glow)
- نوار رنگی ۱۲px بالا → چیپ دسته (وسط) → عنوان درشت Vazirmatn Black (وسط)
  → زیرعنوان رنگی → کارت تصویر گوشه‌گرد با قاب سفید و سایهٔ نرم
  → پلاک نکتهٔ کپسولی هم‌رنگ پالت → نوار پیشرفت تکه‌تکه راست‌به‌چپ
  → پلاک «دکتر کیانوش سالاریان»
- هر اسلاید یک پالت از ۵ پالت ریل: sage/warm/mint/night/clay
- متن فارسی فقط با Vazirmatn و fatext (HarfBuzz)

استفاده:
    from reel45_template import build_carousel, asset
    build_carousel(slug, eyebrow, slides, caption, ov_title=(خط۱, خط۲))
هر اسلاید: dict(palette, image, title, sub, tip, cover=False, cta=None)
خروجی: reels/carousel/<slug>/ اسلایدهای PNG + _overview.png + _caption.txt + _all.zip
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carousel_engine as C  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

W, H = C.W, C.H  # 1080×1350 (۴:۵)
ROOT = C.ROOT
BRAND = C.BRAND

# --- پالت‌های ریل (از reel_engine) -----------------------------------------
PAL = {
    "warm":  dict(bg1=(253, 246, 236), bg2=(247, 231, 218), ink=(31, 42, 61),
                  accent=(214, 92, 76), soft=(236, 214, 200)),
    "night": dict(bg1=(246, 240, 233), bg2=(232, 220, 214), ink=(28, 38, 58),
                  accent=(196, 122, 62), soft=(226, 208, 196)),
    "sage":  dict(bg1=(249, 247, 240), bg2=(231, 236, 228), ink=(30, 46, 54),
                  accent=(72, 122, 104), soft=(214, 226, 214)),
    "mint":  dict(bg1=(247, 248, 242), bg2=(226, 236, 230), ink=(30, 48, 56),
                  accent=(58, 112, 132), soft=(212, 228, 226)),
    "clay":  dict(bg1=(253, 245, 238), bg2=(243, 225, 212), ink=(48, 40, 38),
                  accent=(176, 96, 72), soft=(238, 216, 202)),
}


def asset(name):
    return os.path.join(ROOT, "reels", "assets", name)


def fa(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


# --- رندر یک اسلاید (دقیقاً همان قالب car05 و car06) --------------------------
def slide_reel45(pal, sc, idx, total, eyebrow):
    bg1, bg2 = pal["bg1"], pal["bg2"]
    img = Image.new("RGB", (W, H), bg1)
    d = ImageDraw.Draw(img)
    for y in range(H):
        f_ = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(bg1[k] + (bg2[k] - bg1[k]) * f_)
                                            for k in range(3)))
    img = img.convert("RGBA")

    # هاله‌های نرم (glow ریل، مقیاس‌شده برای ۴:۵)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for (cx, cy, r, a) in ((140, 180, 280, 40), (980, 520, 300, 30),
                           (940, 1050, 260, 26), (120, 1180, 240, 22)):
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))

    d = ImageDraw.Draw(img, "RGBA")
    # نوار رنگی باریک بالای کادر
    d.rounded_rectangle([0, 0, W, 12], 6, fill=(*pal["accent"], 255))

    # چیپ دسته‌بندی (وسط)
    fe = C.font(C.BOLD, 32)
    tw = C.measure(eyebrow, fe)[2]
    cw = tw + 76
    C.rrect(img, [(W - cw) / 2, 54, (W + cw) / 2, 122], 34,
            fill=(255, 255, 255, 215), outline=(*pal["soft"], 255), width=3)
    C.draw_text(img, (W / 2, 88), eyebrow, font=fe,
                fill=(*pal["accent"], 255), anchor="mm")

    # عنوان درشت وسط
    start = 88 if sc.get("cover") else 80
    f_t, lines = C.fit_block(sc["title"], W - 140, 2, start, 50)
    y = C.draw_lines(img, lines, f_t, (*pal["ink"], 255), W / 2, 160,
                     anchor="ma", gap=1.42)

    # زیرعنوان رنگی
    fs = C.font(C.BOLD, 40)
    sub_lines = C.wrap(sc["sub"], fs, W - 170)
    if len(sub_lines) > 2:
        fs = C.font(C.BOLD, 36)
        sub_lines = C.wrap(sc["sub"], fs, W - 170)
    y = C.draw_lines(img, sub_lines, fs, (*pal["accent"], 255), W / 2, y + 6,
                     anchor="ma", gap=1.5)

    # کارت تصویر
    has_cta = bool(sc.get("cta"))
    card_bottom = 1006 if has_cta else 1046
    card_top = int(max(y + 32, 400))
    box = (64, card_top, W - 64, card_bottom)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [box[0] + 2, box[1] + 14, box[2] + 2, box[3] + 18], 42,
        fill=(90, 70, 56, 38))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    crop, mask = C.rounded_image(sc["image"], box, 42, 1.02)
    img.paste(crop, (box[0], box[1]), mask)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle(list(box), 42, outline=(255, 255, 255, 215), width=6)

    # پلاک نکته (pill رنگی ریل)
    f_p = C.font(C.BOLD, 42)
    while C.measure(sc["tip"], f_p)[2] > W - 300 and f_p.size > 32:
        f_p = C.font(C.BOLD, f_p.size - 2)
    pw = C.measure(sc["tip"], f_p)[2] + 104
    ph = 96
    px, py = (W - pw) / 2, card_bottom + 26
    C.rrect(img, [px, py + 8, px + pw, py + ph + 8], ph / 2, fill=(50, 35, 25, 45))
    C.rrect(img, [px, py, px + pw, py + ph], ph / 2, fill=(*pal["accent"], 255))
    C.draw_text(img, (W / 2, py + ph / 2), sc["tip"], font=f_p,
                fill=(255, 255, 255, 255), anchor="mm")

    # خط دعوت (فقط اسلاید آخر)
    if has_cta:
        C.draw_text(img, (W / 2, py + ph + 44), sc["cta"],
                    font=C.font(C.BOLD, 31), fill=(*pal["accent"], 255),
                    anchor="mm")

    # نوار پیشرفت تکه‌تکه راست‌به‌چپ (ترجمهٔ کاروسلیِ نوار پیشرفت ریل)
    seg_y, seg_h, gap = 1242, 12, 10
    seg_w = (W - 128 - (total - 1) * gap) / total
    for i in range(total):
        x0 = W - 64 - (i + 1) * seg_w - i * gap
        fill = (*pal["accent"], 255) if i < idx else (255, 255, 255, 150)
        C.rrect(img, [x0, seg_y, x0 + seg_w, seg_y + seg_h], 6,
                fill=fill, outline=(*pal["soft"], 255), width=2)

    # پلاک نام
    C.draw_text(img, (W / 2, 1300), BRAND, font=C.font(C.MED, 30),
                fill=(*pal["ink"], 150), anchor="mm")
    return img


def build_carousel(slug, eyebrow, slides, caption, ov_title=("", ""),
                   ov_palette="mint"):
    """ساخت کامل کاروسل با قالب قفل‌شده: اسلایدها + نمای کلی + کپشن + ZIP."""
    outdir = os.path.join(C.OUT, slug)
    os.makedirs(outdir, exist_ok=True)
    total = len(slides)
    files = []
    for i, sc in enumerate(slides, start=1):
        img = slide_reel45(PAL[sc["palette"]], sc, i, total, eyebrow)
        p = os.path.join(outdir, f"{slug}_{i:02d}.png")
        img.convert("RGB").save(p, quality=94)
        files.append(p)
        print("saved", os.path.basename(p), img.size,
              f"ratio={img.width / img.height:.3f}", sc["palette"])

    # نمای کلی ۲ ستون راست‌به‌چپ (خانهٔ آخر: کارت عنوان)
    tw, th = 540, 675
    rows = (total + 2) // 2
    ov = Image.new("RGBA", (tw * 2, th * rows), (255, 255, 255, 255))
    for i, p in enumerate(files):
        ov.paste(Image.open(p).resize((tw, th), Image.LANCZOS),
                 ((1 - i % 2) * tw, (i // 2) * th))
    p_ov = PAL[ov_palette]
    cell = Image.new("RGBA", (tw, th), (*p_ov["bg2"], 255))
    f1, f2, f3 = C.font(C.BLACK, 40), C.font(C.BOLD, 27), C.font(C.MED, 25)
    C.draw_text(cell, (tw / 2, th / 2 - 90), ov_title[0], font=f1,
                fill=(*p_ov["ink"], 255), anchor="mm")
    C.draw_text(cell, (tw / 2, th / 2 - 34), ov_title[1], font=f1,
                fill=(*p_ov["ink"], 255), anchor="mm")
    C.draw_text(cell, (tw / 2, th / 2 + 28),
                f"کاروسل {fa(total)} اسلایدی • سبک ریل • ۴:۵",
                font=f2, fill=(*p_ov["accent"], 255), anchor="mm")
    C.draw_text(cell, (tw / 2, th / 2 + 84), BRAND, font=f3,
                fill=(*p_ov["ink"], 170), anchor="mm")
    ov.paste(cell, ((1 - total % 2) * tw, (total // 2) * th))
    ov_path = os.path.join(outdir, f"{slug}_overview.png")
    ov.convert("RGB").save(ov_path, quality=94)
    print("saved", os.path.basename(ov_path), ov.size)

    cap_path = os.path.join(outdir, f"{slug}_caption.txt")
    with open(cap_path, "w", encoding="utf-8") as f:
        f.write(caption)

    zip_path = os.path.join(outdir, f"{slug}_all.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files + [cap_path]:
            z.write(p, os.path.basename(p))
    print(f"[✓] {slug}: {total} اسلاید سبک ریل (۴:۵) + کپشن + ZIP → {outdir}")
    return outdir, files, ov_path, cap_path, zip_path
