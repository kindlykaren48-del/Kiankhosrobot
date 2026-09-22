#!/usr/bin/env python3
"""
بررسی خروجی نهایی ریل — مشخصات را از خود فایل می‌خواند، نه از نام یا تنظیمات.

استفاده:
    python3 check_output.py <reel.mp4> [حداکثر_حجم_MB] [حداقل_مدت] [حداکثر_مدت]

معیارهای استاندارد پروژه: ۱۰۸۰×۱۹۲۰ · ۳۰ فریم · حداکثر ۴ مگابایت · صدا دارد.
"""
import os, re, subprocess, sys
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()


def probe(path):
    """اطلاعات فایل را با ffmpeg (بدون ffprobe) استخراج می‌کند."""
    out = subprocess.run([FF, "-hide_banner", "-i", path],
                         capture_output=True).stderr.decode("utf-8", "ignore")
    info = {"duration": None, "fps": None, "size": None, "has_audio": None,
            "vcodec": None, "acodec": None}
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if m:
        h, mi, s = m.groups()
        info["duration"] = int(h) * 3600 + int(mi) * 60 + float(s)
    m = re.search(r"(\d+(?:\.\d+)?) fps", out)
    if m:
        info["fps"] = float(m.group(1))
    m = re.search(r"Video: (\w+)", out)
    if m:
        info["vcodec"] = m.group(1)
    m = re.search(r"Stream #\d+:\d+.*: Video: .*?, (\d{3,5})x(\d{3,5})", out)
    if m:
        info["size"] = (int(m.group(1)), int(m.group(2)))
    else:
        m = re.search(r"(\d{3,5})x(\d{3,5})", out)
        if m:
            info["size"] = (int(m.group(1)), int(m.group(2)))
    m = re.search(r"Audio: (\w+)", out)
    info["has_audio"] = bool(m)
    if m:
        info["acodec"] = m.group(1)
    info["bytes"] = os.path.getsize(path)
    return info


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    max_mb = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
    min_d = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    max_d = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
    i = probe(path)
    mb = i["bytes"] / 1048576
    checks = []
    checks.append(("فایل موجود است", os.path.isfile(path)))
    checks.append((f"حجم {mb:.2f}MB ≤ {max_mb}MB", mb <= max_mb))
    checks.append((f"وضوح {i['size']} == (1080, 1920)", i["size"] == (1080, 1920)))
    checks.append((f"فریم‌ریت {i['fps']} ≈ 30", i["fps"] is not None and abs(i["fps"] - 30) < 0.6))
    checks.append((f"مدت {i['duration']:.2f}s بین {min_d} و {max_d}",
                   i["duration"] is not None and min_d <= i["duration"] <= max_d))
    checks.append((f"صدا دارد ({i['acodec']})", bool(i["has_audio"])))
    print(f"--- بررسی {path} ---")
    ok = True
    for name, good in checks:
        print(("  ✔ " if good else "  ✘ ") + name)
        ok = ok and good
    print("نتیجه:", "قابل تحویل" if ok else "مشکل دارد")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
