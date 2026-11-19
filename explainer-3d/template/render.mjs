// render.mjs — رندر قطعی ۲۵ ثانیه‌ای با Playwright + FFmpeg
// خروجی: output.mp4 (1920x1080, 60fps) — اگر voiceover.mp3 کنار این فایل باشد، میکس می‌شود.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const DURATION = 25;          // ثانیه
const FPS = 60;
const W = 1920, H = 1080;
const FRAMES = DURATION * FPS;
const VOICEOVER = path.join(DIR, 'voiceover.mp3');

const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.goto('file://' + path.join(DIR, 'index.html'));
await page.waitForFunction(() => typeof window.renderAtTime === 'function');
await page.waitForTimeout(1500); // اجازه بارگذاری فونت/Three.js

// FFmpeg: ورودی خام از stdin
const ffmpegArgs = [
  '-y',
  '-f', 'image2pipe', '-vcodec', 'png', '-r', String(FPS), '-i', '-',
];
if (existsSync(VOICEOVER)) {
  ffmpegArgs.push('-i', VOICEOVER);
  ffmpegArgs.push('-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-shortest');
} else {
  ffmpegArgs.push('-an');
}
ffmpegArgs.push(
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', String(FPS),
  '-movflags', '+faststart',
  path.join(DIR, 'output.mp4')
);

const ffmpeg = spawn('ffmpeg', ffmpegArgs, { stdio: ['pipe', 'inherit', 'inherit'] });
ffmpeg.stdin.on('error', (e) => { console.error('ffmpeg stdin error:', e.message); });

for (let i = 0; i < FRAMES; i++) {
  const t = i / FPS;
  await page.evaluate((tt) => window.renderAtTime(tt), t);
  const buf = await page.screenshot({ type: 'png' });
  if (!ffmpeg.stdin.write(buf)) {
    await new Promise((res) => ffmpeg.stdin.once('drain', res));
  }
  if (i % 60 === 0) console.log(`frame ${i}/${FRAMES} (t=${t.toFixed(2)}s)`);
}

ffmpeg.stdin.end();
await new Promise((res, rej) => {
  ffmpeg.on('close', (code) => (code === 0 ? res() : rej(new Error('ffmpeg exit ' + code))));
});
await browser.close();
console.log('✅ output.mp4 ساخته شد:', path.join(DIR, 'output.mp4'));
