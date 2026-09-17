"""
fatext.py — شکل‌دهی و رندر متن فارسی برای Pillow بدون نیاز به libraqm
(HarfBuzz + FreeType / uharfbuzz + freetype-py)

جایگزین سبکِ موتور Raqm: متن با HarfBuzz چیده می‌شود (اتصال حروف، لیگاتور،
کرنینگ، جهت راست‌به‌چپ) و گلیف‌ها با FreeType رستر می‌شوند.

استفاده:
    from fatext import FD
    d = FD(img)              # به‌جای ImageDraw.Draw(img)
    d.text((100, 200), "سلام دنیا", font=f, fill=(255, 255, 255), anchor="mm")
اندازه‌گیری: d.textbbox((x, y), txt, font=f, anchor="mm")
"""
from __future__ import annotations

import numpy as np
import freetype
import uharfbuzz as hb
from PIL import Image, ImageDraw

# ---------------------------------------------------------------- caches
_hb_fonts: dict[str, hb.Font] = {}
_hb_blobs: dict[str, hb.Blob] = {}
_ft_faces: dict[tuple[str, int], freetype.Face] = {}
_ident = freetype.Matrix(0x10000, 0, 0, 0x10000)


def _hb_font(path: str) -> hb.Font:
    if path not in _hb_fonts:
        blob = hb.Blob.from_file_path(path)
        face = hb.Face(blob)
        _hb_blobs[path] = blob
        _hb_fonts[path] = hb.Font(face)
    return _hb_fonts[path]


def _ft_face(path: str, size: int) -> freetype.Face:
    key = (path, size)
    if key not in _ft_faces:
        f = freetype.Face(path)
        f.set_char_size(int(round(size * 64)))
        _ft_faces[key] = f
    return _ft_faces[key]


def _is_rtl(t: str) -> bool:
    for ch in t:
        o = ord(ch)
        if 0x0590 <= o <= 0x08FF or 0xFB1D <= o <= 0xFEFF:
            return True
    return False


# ------------------------------------------------------------ bidi (سبک UAX#9)
def _cls(ch: str) -> str:
    o = ord(ch)
    # ارقام باید چپ‌به‌راست بمانند، وگرنه «۱۲۳» به‌صورت «۳۲۱» درمی‌آید
    if (0x30 <= o <= 0x39 or 0x0660 <= o <= 0x0669 or 0x06F0 <= o <= 0x06F9
            or 0x41 <= o <= 0x5A or 0x61 <= o <= 0x7A or 0x00C0 <= o <= 0x024F):
        return "L"          # لاتین و همهٔ ارقام
    if 0x0590 <= o <= 0x08FF or 0xFB1D <= o <= 0xFEFF:
        return "R"          # عبری/عربی/فارسی
    return "W"              # فاصله، نقطه‌گذاری، نیم‌فاصله، نماد


def bidi_runs(text: str):
    """متن را به قطعه‌های هم‌جهت تقسیم می‌کند و به ترتیب دیداری (چپ→راست)
    برمی‌گرداند: فهرستی از (متن_قطعه, rtl)."""
    if not text:
        return []
    cls = [_cls(c) for c in text]
    # جهت پایه: نخستین نویسهٔ قوی
    base = "R"
    for c in cls:
        if c in ("R", "L"):
            base = c
            break
    # حل نویسه‌های ضعیف (فاصله و نقطه‌گذاری)
    out = cls[:]
    i = 0
    while i < len(cls):
        if cls[i] == "W":
            j = i
            while j < len(cls) and cls[j] == "W":
                j += 1
            left = out[i-1] if i > 0 else None
            right = out[j] if j < len(out) else None
            fill = left if left == right and left else base
            for k in range(i, j):
                out[k] = fill
            i = j
        else:
            i += 1
    # قطعه‌بندی
    runs, cur, cur_type = [], "", out[0]
    for ch, t in zip(text, out):
        if t == cur_type:
            cur += ch
        else:
            runs.append((cur, cur_type))
            cur, cur_type = ch, t
    runs.append((cur, cur_type))
    runs = [(t, ty == "R") for t, ty in runs]
    if base == "R":
        runs.reverse()      # پاراگراف راست‌به‌چپ: ترتیب قطعه‌ها معکوس می‌شود
    return runs


# ---------------------------------------------------------------- shaping
def shape(text: str, path: str, size: int, rtl: bool | None = None,
          features: dict | None = None):
    """متن را با HarfBuzz می‌چیند و گلیف‌ها را با موقعیت برمی‌گرداند.
    خروجی: (glyphs, advance) که glyphs فهرستی از (gid, x, y) بر حسب پیکسل است."""
    rtl_text = _is_rtl(text)
    if rtl is None:
        rtl = rtl_text
    font = _hb_font(path)
    font.scale = (int(size * 64), int(size * 64))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction = "rtl" if rtl else "ltr"
    buf.script = "Arab" if rtl_text else "Latn"
    buf.language = "fa" if rtl_text else "en"
    if features:
        hb.shape(font, buf, features)
    else:
        hb.shape(font, buf)
    glyphs, x, y = [], 0.0, 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        xo = pos.x_offset / 64.0
        yo = pos.y_offset / 64.0
        glyphs.append((info.codepoint, x + xo, y + yo))
        x += pos.x_advance / 64.0
        y += pos.y_advance / 64.0
    return glyphs, x


def layout(text: str, path: str, size: int, rtl: bool | None = None):
    """returns (glyphs, advance, ascent, descent)"""
    glyphs, adv = shape(text, path, size, rtl)
    ft = _ft_face(path, size)
    return glyphs, adv, ft.size.ascender / 64.0, ft.size.descender / 64.0


# ---------------------------------------------------------------- raster
def _glyph_masks(glyphs, path: str, size: int):
    """هر گلیف را رستر می‌کند: فهرست (x, y, array) با مختصات نسبت به خط پایه."""
    ft = _ft_face(path, size)
    out = []
    for gid, gx, gy in glyphs:
        xi = int(np.floor(gx))
        frac = int(round((gx - xi) * 64)) & 0x3F
        ft.set_transform(_ident, freetype.Vector(frac, 0))
        try:
            ft.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL
                          | freetype.FT_LOAD_NO_HINTING)
        except Exception:
            continue
        bmp = ft.glyph.bitmap
        if bmp.width == 0 or bmp.rows == 0:
            continue
        pitch = abs(bmp.pitch)
        arr = np.frombuffer(bytes(bmp.buffer), dtype=np.uint8,
                            count=bmp.rows * pitch).reshape(bmp.rows, pitch)
        if bmp.pitch < 0:
            arr = arr[::-1]
        arr = arr[:, :bmp.width]
        if bmp.pixel_mode == 1:      # mono -> 0/255
            arr = np.unpackbits(arr, axis=1)[:, :bmp.width] * 255
        out.append((xi + ft.glyph.bitmap_left, int(round(gy)) - ft.glyph.bitmap_top, arr))
    ft.set_transform(_ident, freetype.Vector(0, 0))
    return out


def render_mask(text: str, path: str, size: int, rtl: bool | None = None):
    """رندر متن روی ماسک L با ابعاد دقیق جوهر.
    خروجی: (mask, x0, y0, advance, ascent, descent)
    x0,y0 مکان گوشهٔ بالا-چپ ماسک نسبت به نقطهٔ شروع خط و خط پایه است."""
    if not text:
        return Image.new("L", (1, 1), 0), 0.0, 0.0, 0.0, 0.0, 0.0
    ft = _ft_face(path, size)
    asc, desc = ft.size.ascender / 64.0, ft.size.descender / 64.0
    if rtl is None:
        runs = bidi_runs(text)
    else:
        runs = [(text, bool(rtl))]
    glyphs, adv_total = [], 0.0
    for run_text, run_rtl in runs:
        glyphs_run, adv_run = shape(run_text, path, size, run_rtl)
        glyphs += [(gid, gx + adv_total, gy) for gid, gx, gy in glyphs_run]
        adv_total += adv_run
    adv = adv_total
    pieces = _glyph_masks(glyphs, path, size)
    if not pieces:
        return Image.new("L", (1, 1), 0), 0.0, 0.0, adv, asc, desc
    x0 = min(p[0] for p in pieces)
    y0 = min(p[1] for p in pieces)
    x1 = max(p[0] + p[2].shape[1] for p in pieces)
    y1 = max(p[1] + p[2].shape[0] for p in pieces)
    canvas = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
    for px, py, arr in pieces:
        h, w = arr.shape
        sl = canvas[py - y0:py - y0 + h, px - x0:px - x0 + w]
        np.maximum(sl, arr, out=sl)
    return Image.fromarray(canvas, "L"), float(x0), float(y0), adv, asc, desc


def _font_info(font):
    """مسیر و اندازهٔ فونت را از یک شیء Pillow FreeTypeFont یا دیکشنری می‌گیرد."""
    if isinstance(font, dict):
        return font["path"], int(font["size"])
    path = getattr(font, "path", None)
    size = getattr(font, "size", None)
    if isinstance(path, bytes):
        path = path.decode()
    if path is None or size is None:
        raise ValueError("fatext: font must be a FreeTypeFont (path/size)")
    return path, int(size)


def _offsets(anchor, xy, bbox, adv, asc, desc):
    """مکان (origin_x, baseline) و جعبهٔ نهایی را بر اساس لنگر Pillow برمی‌گرداند."""
    anchor = anchor or "la"
    h, v = anchor[0], anchor[1]
    x0, y0, x1, y1 = bbox
    if h == "l":
        ox = xy[0]
    elif h == "m":
        ox = xy[0] - adv / 2.0
    elif h == "r":
        ox = xy[0] - adv
    else:
        ox = xy[0]
    if v == "a":
        base = xy[1] + asc
    elif v == "t":
        base = xy[1] - y0
    elif v == "m":
        base = xy[1] + (asc + desc) / 2.0
    elif v == "s":
        base = xy[1]
    elif v == "b":
        base = xy[1] - y1
    elif v == "d":
        base = xy[1] + desc
    else:
        base = xy[1]
    box = (int(round(ox + x0)), int(round(base + y0)),
           int(round(ox + x1)), int(round(base + y1)))
    return ox, base, box


def measure(text, font, anchor="la", rtl=None):
    """جعبهٔ متن بدون رسم، دقیقاً مانند ImageDraw.textbbox"""
    path, size = _font_info(font)
    if not text:
        return (0, 0, 0, 0)
    mask, x0, y0, adv, asc, desc = render_mask(text, path, size, rtl)
    x1 = x0 + mask.width
    y1 = y0 + mask.height
    _, _, box = _offsets(anchor, (0, 0), (x0, y0, x1, y1), adv, asc, desc)
    return (box[0] - 0, box[1] - 0, box[2], box[3])


def _fill_rgba(fill, a=255):
    if fill is None:
        fill = (255, 255, 255, a)
    if isinstance(fill, int):
        return (fill, fill, fill, a)
    if len(fill) == 3:
        return (fill[0], fill[1], fill[2], a)
    return (fill[0], fill[1], fill[2], fill[3])


def draw_text(image, xy, text, font=None, fill=None, anchor=None, rtl=None, **kw):
    """رسم متن روی تصویر (RGB یا RGBA) با شکل‌دهی صحیح فارسی."""
    if not text:
        return (0, 0, 0, 0)
    path, size = _font_info(font)
    mask, x0, y0, adv, asc, desc = render_mask(text, path, size, rtl)
    x1, y1 = x0 + mask.width, y0 + mask.height
    ox, base, box = _offsets(anchor, xy, (x0, y0, x1, y1), adv, asc, desc)
    r, g, b, a = _fill_rgba(fill)
    px, py = int(round(ox + x0)), int(round(base + y0))
    if a < 255:
        m = mask.point(lambda v: (v * a) // 255)
    else:
        m = mask
    if image.mode == "RGBA":
        layer = Image.new("RGBA", mask.size, (r, g, b, 0))
        layer.putalpha(m)
        image.alpha_composite(layer, (px, py))
    else:
        solid = Image.new("RGB", mask.size, (r, g, b))
        image.paste(solid, (px, py), m)
    return box


class FD:
    """پروکسی ImageDraw که متون فارسی را با HarfBuzz می‌چیند.
    سایر متدها (ellipse/rectangle/line/…) دست‌نخورده به ImageDraw پاس می‌شوند."""

    def __init__(self, image, mode=None):
        self.image = image
        self._d = ImageDraw.Draw(image, mode) if mode else ImageDraw.Draw(image)

    def __getattr__(self, name):
        return getattr(self._d, name)

    def text(self, xy, text, font=None, fill=None, anchor=None, **kw):
        return draw_text(self.image, xy, text, font=font, fill=fill, anchor=anchor, **kw)

    def textbbox(self, xy, text, font=None, anchor=None, **kw):
        if not text:
            return (xy[0], xy[1], xy[0], xy[1])
        path, size = _font_info(font)
        mask, x0, y0, adv, asc, desc = render_mask(text, path, size)
        x1, y1 = x0 + mask.width, y0 + mask.height
        ox, base, box = _offsets(anchor, xy, (x0, y0, x1, y1), adv, asc, desc)
        return box

    def textlength(self, text, font=None, **kw):
        if not text:
            return 0
        path, size = _font_info(font)
        _, adv = shape(text, path, size)
        return adv

    def text_mask(self, text, font, anchor=None, xy=(0, 0)):
        path, size = _font_info(font)
        mask, x0, y0, adv, asc, desc = render_mask(text, path, size)
        ox, base, box = _offsets(anchor, xy, (x0, y0, x0 + mask.width, y0 + mask.height),
                                 adv, asc, desc)
        return mask, (int(round(ox + x0)), int(round(base + y0)))
