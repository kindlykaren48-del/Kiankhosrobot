#!/usr/bin/env bash
# آماده‌سازی محیط ساخت ریل (هر چت جدید یک بار اجرا کن)
set -e
pip install -q --break-system-packages imageio-ffmpeg numpy pillow uharfbuzz freetype-py 2>/dev/null \
  || pip install -q imageio-ffmpeg numpy pillow uharfbuzz freetype-py

# فونت وزیرمتن (در مخزن نیست)
if [ ! -f /home/user/fonttmp/fonts/ttf/Vazirmatn-Bold.ttf ]; then
  mkdir -p /home/user/fonttmp
  curl -sL -o /tmp/vazir.zip https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip
  unzip -qo /tmp/vazir.zip -d /home/user/fonttmp
fi

python3 - <<'PY'
from PIL import features
import imageio_ffmpeg, numpy, PIL
try:
    import uharfbuzz, freetype           # noqa
    fa = "HarfBuzz (fatext.py)"
except Exception:
    fa = "libraqm" if features.check("raqm") else "!! هیچکدام — متن فارسی خراب می‌شود"
print("deps ok | ffmpeg:", imageio_ffmpeg.get_ffmpeg_exe())
print("engine متن فارسی:", fa)
PY
