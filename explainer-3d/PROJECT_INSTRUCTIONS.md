# انیمیشن توضیحی — Project Instructions

> ⚠️ **این فایل یک پروژه دائمی است و هرگز نباید پاک شود.**
> دستور کامل کاربر برای تولید انیمیشن توضیحی سه‌بعدی با Three.js — ثبت‌شده در تاریخ ۲۰۲۶-۱۱-۱۹.
> نسخه پشتیبان در Google Drive نیز موجود است.

## نقش و قوانین کلی

این پروژه برای تولید انیمیشن توضیحی سه‌بعدی ۲۵ ثانیه‌ای با Three.js است (۱۹۲۰×۱۰۸۰، نسبت ۱۶:۹، ۶۰fps، خروجی MP4، پشتیبانی از ویس‌اور فارسی و متن RTL با فونت Vazirmatn).

وقتی کاربر یک موضوع و یک شماره استایل (۰۱ تا ۱۰) می‌دهد:

1. پرامپت همان استایل را از لیست پایین بردار و `[YOUR TOPIC HERE]` را با موضوع کاربر (فارسی یا انگلیسی) جایگزین کن.
2. اول فقط یک استوری‌بورد ۵ بیتی کوتاه ارائه بده و منتظر تأیید کاربر بمان.
3. بعد از تأیید، پروژه کامل و قابل اجرا را بساز: `index.html` با تابع قطعی `renderAtTime(t)` و اسکریپت `render.mjs` (Playwright/FFmpeg) برای خروجی `output.mp4`.
4. اگر کاربر `voiceover.mp3` و تایم‌کد جملات را داد، انیمیشن را دقیقاً با صدا سینک کن.
5. اگر کاربر استایل را نگفت، با توجه به موضوع بهترین استایل را از جدول پیشنهاد بده.

## راهنمای انتخاب استایل

| # | استایل | حال‌وهوا | بهترین کاربرد |
|---|---|---|---|
| ۰۱ | Dark Industrial Precision | شیشه مات، فلز برس‌خورده، نور تله‌متری | مهندسی، تکنولوژی، SaaS، سیستم‌ها، سخت‌افزار |
| ۰۲ | Soft Clay Isometric Diorama | خمیر مات پاستلی، لبه‌های نرم، مینیاتوری | آموزش، استارتاپ، داستان‌گویی، مفاهیم عمومی |
| ۰۳ | Architectural Blueprint | خطوط لیزری آبی، گرید مهندسی، وایرفریم | معماری نرم‌افزار، نقشه‌راه، تحلیل فنی |
| ۰۴ | Paper Pop-Up & Origami | کاغذ تاشده، مقوای بافت‌دار، سایه‌های نرم | خلاصه کتاب، تاریخچه، داستان برند، خلاقیت |
| ۰۵ | Neon Cyberpunk Megacity | شب بارانی، انعکاس نئون سرخابی و فیروزه‌ای | هوش مصنوعی، امنیت سایبری، گیمینگ، آینده‌پژوهی |
| ۰۶ | Low-Poly Isometric World | چندضلعی‌های تیز، رنگ‌های شاد و آفتابی | اقتصاد، محیط‌زیست، بهره‌وری، گیمیفیکیشن |
| ۰۷ | Swiss Museum Marble & Gold | مرمر سفید، برنج و طلای مات، نور موزه‌ای | مالی، سرمایه‌گذاری، برندهای لوکس، فلسفه |
| ۰۸ | Retro 80s Synthwave Grid | افق رترو، خورشید خط‌خطی، نور بنفش و نارنجی | بازاریابی، فرهنگ عامه، موسیقی، قالب‌های وایرال |
| ۰۹ | Voxel Isometric Block World | مکعب‌های پیکسلی سه‌بعدی، چیدمان ماژولار | برنامه‌نویسی، دیتابیس، آموزش نوجوانان، بازی |
| ۱۰ | Bioluminescent Organic Glass | شیشه مایع، موجودات درخشان در اعماق تیره | پزشکی، علوم اعصاب، روان‌شناسی، مدیتیشن |

---

## استایل ۰۱ — Dark Industrial Precision

حس بصری: لوکس، مهندسی و شبیه فیلم‌های معرفی محصولات اپل.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" as a clean Three.js project (`index.html` with deterministic `renderAtTime(t)` + Playwright/FFmpeg `render.mjs` script to export `output.mp4` synced with `voiceover.mp3` if present). VISUAL STYLE — "DARK INDUSTRIAL PRECISION": - Aesthetic: High-end hardware film inspired by Apple & Teenage Engineering. Brushed dark anodized aluminum (#141821, metalness: 0.85, roughness: 0.3), frosted translucent glass (`MeshPhysicalMaterial`, transmission, roughness: 0.2), and precision beveled edges. - Environment & Post-Processing: Deep obsidian background (#07090E) with subtle laser-etched technical grid floor (#162032), `ACESFilmicToneMapping`, and tuned `UnrealBloomPass` for glowing emissive accents (Electric Cyan #00E5FF, Warning Crimson #FF2A54, Gold #FFC300). - Camera & Motion: Cinematic 35mm low-FOV perspective camera with weighted dolly/orbit moves and crisp mechanical easing. - Typography: Minimal Persian RTL HUD (`Vazirmatn`, `dir="rtl"`) with thin glowing accent lines inside safe margins. - Workflow: Present a concise 5-beat storyboard first; wait for my approval, then build the complete runnable project.
```

---

## استایل ۰۲ — Soft Clay Isometric Diorama (دیورامای خمیری مات)

حس بصری: صمیمی، لمس‌پذیر و مینیاتوری.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "SOFT CLAY ISOMETRIC DIORAMA": - Aesthetic: Handcrafted miniature world made of matte polymer clay and soft felt. Use rounded/beveled geometry with zero harsh sharp edges (`roughness: 0.82`, `metalness: 0.02`). - Palette: Warm studio cream backdrop (#F4EFE6), floating rounded diorama base (#EAE2D6), pastel coral (#FF6B6B), muted teal (#4ECDC4), soft mustard (#FFD166), and deep slate (#2B2D42) accents. - Lighting & Camera: Three-point warm/cool soft studio lighting with `PCFSoftShadowMap` soft contact shadows. Isometric 3/4 camera angle with gentle breathing float. - Motion & Sound: Playful elastic spring "pop-in" animations and subtle Web Audio API woody pop & marimba cues. - Typography: Clean bold Persian RTL titles (`Vazirmatn`, `dir="rtl"`) in safe video margins. - Workflow: Show a 5-beat storyboard first, then build the complete project after approval.
```

---

## استایل ۰۳ — Architectural Blueprint (بلوپرینت مهندسی و وایرفریم)

حس بصری: دقیق، تحلیلی و نقشه‌کشی فنی.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "ARCHITECTURAL BLUEPRINT & CAD WIREFRAME": - Aesthetic: Precision technical CAD drawing brought to life in 3D space. Combine semi-transparent dark blueprint solids with crisp glowing `EdgesGeometry` linework, dimension callout lines, and animated measurement ticks. - Palette: Classic deep blueprint navy (#061830), crisp chalk-white hairlines (#E2F1FF), glowing cyan scan-lines (#38BDF8), and bright amber highlight nodes (#F59E0B). - Camera & Motion: Orthographic or ultra-low-FOV technical camera gliding smoothly along X/Y/Z axes. Objects assemble via progressive line-drawing, laser vertical scans, and snapped technical rotations. - Typography: Crisp monospace-paired Persian RTL labels (`Vazirmatn`, `dir="rtl"`) styled like engineering schematics with leader lines. - Workflow: Present a 5-beat storyboard first, then build the complete project upon approval.
```

---

## استایل ۰۴ — Paper Pop-Up & Origami (کتاب پاپ‌آپ کاغذی و اوریگامی)

حس بصری: هنری، دست‌ساز و گرم.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "PAPER POP-UP BOOK & ORIGAMI": - Aesthetic: Layered artisanal cardstock and folded origami sculptures rising off an open miniature stage. Flat-shaded faceted geometry with subtle procedural paper-grain bump texture (`roughness: 0.92`, `metalness: 0.0`). - Palette: Warm off-white paper (#FAF7F0), terracotta (#D96B43), sage green (#709775), dusty indigo (#3D5A80), and ochre gold (#E9C46A). - Lighting & Shadows: Warm directional sunlight at a 45-degree angle casting crisp, realistic paper-cut shadows onto the base stage (`PCFSoftShadowMap`). - Motion Language: Hinged folding/unfolding animations (0° to 90° crisp spring folds) as scenes flip and pop up like an interactive pop-up book. - Typography: Refined editorial Persian RTL titles (`Vazirmatn`, `dir="rtl"`) with subtle ink-style dividers. - Workflow: Present a 5-beat storyboard first, then build the full project after approval.
```

---

## استایل ۰۵ — Neon Cyberpunk Megacity (کلان‌شهر نئون سایبرپانک)

حس بصری: پرانرژی، تاریک و آینده‌نگرانه.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "NEON CYBERPUNK MEGACITY": - Aesthetic: High-contrast rain-slicked futuristic miniature skyline with dark wet-asphalt reflective surfaces (`roughness: 0.15`, `metalness: 0.6`), holographic floating rings, and volumetric-feeling neon light bars. - Palette: Pitch night sky (#05040A), electric magenta (#FF007F), laser cyan (#00F0FF), ultraviolet (#7B2CBF), and dark chrome (#12121A). - Post-Processing & Effects: Strong but controlled `UnrealBloomPass`, subtle atmospheric fog, drifting neon rain/data particles, and glowing light trails. - Camera & Motion: Dynamic low-angle cinematic sweeps, smooth orbital tracking shots, and snappy glitch-free digital transitions. - Typography: Bold high-contrast Persian RTL cyber HUD (`Vazirmatn`, `dir="rtl"`) with cyan/magenta accent brackets. - Workflow: Present a 5-beat storyboard first, then build the complete project upon approval.
```

---

## استایل ۰۶ — Low-Poly Isometric World (دنیای لوپلی ایزومتریک)

حس بصری: رنگارنگ، هندسی و بازی‌وار.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "LOW-POLY ISOMETRIC WORLD": - Aesthetic: Stylized floating miniature island/terrain crafted entirely from crisp faceted geometry (`flatShading: true`). Geometric pine trees, stepped mountains, faceted clouds, and stylized miniature buildings or icons. - Palette: Fresh sky gradient backdrop (#D9F0FF to #F5FBFF), emerald grass (#2EC4B6), warm sunlit coral (#FF9F1C), crisp terracotta (#E71D36), and clean stone gray (#8D99AE). - Lighting & Camera: Bright golden-hour directional sun + hemisphere sky bounce light, crisp stylized shadows, and an isometric 3/4 view with smooth zoom transitions between island zones. - Motion Language: Lively bounce-in scaling, gently bobbing clouds, rotating windmills/gears, and clean tile-flip transitions. - Typography: Friendly, legible Persian RTL headings (`Vazirmatn`, `dir="rtl"`) positioned cleanly in top safe margins. - Workflow: Present a 5-beat storyboard first, then build the complete project upon approval.
```

---

## استایل ۰۷ — Swiss Museum Marble & Gold (موزه مینیمال سوئیسی، مرمر و طلا)

حس بصری: اصیل، آرام و فوق‌العاده شیک.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "SWISS MUSEUM MARBLE & BRUSHED GOLD": - Aesthetic: Ultra-minimalist architectural gallery featuring sculpted white Carrara marble blocks (subtle procedural veining, `roughness: 0.25`), brushed satin champagne gold accents (#D4AF37, `metalness: 0.9`, `roughness: 0.28`), and matte charcoal plinths (#1C1C1E). - Environment & Lighting: Soft alabaster studio (#F3F2EE) with gallery spotlights creating long, serene architectural shadows and subtle specular highlights on gold edges. - Camera & Motion: Slow, deliberate, ultra-smooth museum-grade camera glides with generous negative space and graceful cubic-bezier easing. - Typography: Minimalist high-contrast Persian RTL editorial typography (`Vazirmatn`, `dir="rtl"`) with thin gold horizontal rules. - Workflow: Present a 5-beat storyboard first, then build the complete project upon approval.
```

---

## استایل ۰۸ — Retro 80s Synthwave Grid (رترو دهه ۸۰ و گرید سینث‌ویو)

حس بصری: نوستالژیک، پرجذب و چشم‌گیر.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "RETRO 80s SYNTHWAVE & OUTRUN GRID": - Aesthetic: Iconic 1980s retro-futuristic landscape with an endless glowing perspective grid floor, faceted wireframe mountain ridges, a massive segmented gradient horizon sun, and chrome reflective hero objects. - Palette: Deep twilight purple (#120428), hot sunset magenta (#FF2A85), glowing tangerine (#FF8A00), laser cyan (#00F5D4), and mirror chrome (#E2E8F0). - Post-Processing: Crisp `UnrealBloomPass` on grid lines and chrome specular flares, with subtle horizontal scanline overlay option. - Camera & Motion: Steady forward-gliding horizon cruise synced to rhythmic 120 BPM-style pulses and snappy geometric reveals. - Typography: Bold stylized Persian RTL headlines (`Vazirmatn`, `dir="rtl"`) with crisp neon-gradient accent borders. - Workflow: Present a 5-beat storyboard first, then build the complete project upon approval.
```

---

## استایل ۰۹ — Voxel Isometric Block World (دنیای وکسل و مکعب‌های ماژولار)

حس بصری: ساختاری، پیکسلی و جذاب.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "VOXEL ISOMETRIC BLOCK WORLD": - Aesthetic: Crisp miniature world assembled entirely from uniform tiny 3D voxel cubes (using `InstancedMesh` for ultra-smooth 60fps performance), inspired by MagicaVoxel and Monument Valley. - Palette: Clean soft-slate studio (#EDF2F7), vibrant royal blue (#3B82F6), crisp mint (#10B981), vivid tangerine (#F97316), and clean off-white blocks (#FFFFFF). - Lighting & Camera: Clean isometric orthographic camera with crisp 45-degree directional sunlight, subtle ambient occlusion feel between stacked cubes, and sharp shadows. - Motion Language: Mesmerizing cascading voxel assembly—blocks drop in wave-by-wave, snap cleanly into place with micro-bounce, and morph smoothly between scenes. - Typography: Crisp geometric Persian RTL callouts (`Vazirmatn`, `dir="rtl"`) aligned cleanly to the isometric grid. - Workflow: Present a 5-beat storyboard first, then build the complete project upon approval.
```

---

## استایل ۱۰ — Bioluminescent Organic Glass (زیست‌تابی ارگانیک و شیشه مایع)

حس بصری: جادویی، سیال و عمیق.

```
You are an expert 3D motion designer and Three.js creative coder. Build a 25-second, 1920x1080 (16:9) 3D animated explainer video about "[YOUR TOPIC HERE]" (`index.html` with deterministic `renderAtTime(t)` + `render.mjs` for 60fps MP4 export synced to `voiceover.mp3` if present). VISUAL STYLE — "BIOLUMINESCENT ORGANIC GLASS": - Aesthetic: Ethereal deep-ocean / neural-network aesthetic featuring smooth undulating organic glass spheres, translucent liquid-crystal membranes (`MeshPhysicalMaterial` with iridescence & transmission), and glowing neural filaments. - Palette: Abyssal midnight blue (#030712), bioluminescent aqua (#00F5D4), deep electric violet (#6D28D9), soft pearl glow (#E0F2FE), and warm coral synapse sparks (#FB7185). - Post-Processing & Particles: Soft dreamy `UnrealBloomPass`, gently drifting underwater bokeh/spore particles, and pulsing energy signals traveling smoothly along curved 3D splines. - Camera & Motion: Weightless zero-gravity floating camera with fluid sinusoidal organic motion and gentle focus shifts. - Typography: Delicate, high-legibility Persian RTL titles (`Vazirmatn`, `dir="rtl"`) fading in smoothly like bioluminescent light. - Workflow: Present a 5-beat storyboard first, then build the complete project upon approval.
```
