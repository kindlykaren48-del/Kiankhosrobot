from __future__ import annotations

"""Build a five-slide, multicolor 4:5 carousel from cinematic 3D illustrations."""

import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "baby_smarter_pixar_assets"
OUT = ROOT / "baby_smarter_pixar_carousel"
sys.path.insert(0, str(ROOT / "toolkit"))
from fatext import FD  # type: ignore

S = 2
W, H = 1080*S, 1350*S
FONT_DIR = ROOT.parent / "fonttmp" / "fonts" / "ttf"
F_REG = "Vazirmatn-Regular.ttf"
F_MED = "Vazirmatn-Medium.ttf"
F_BOLD = "Vazirmatn-Bold.ttf"
F_BLACK = "Vazirmatn-Black.ttf"

NAVY=(21,28,53); WHITE=(255,255,255); CREAM=(255,248,233)
PURPLE=(120,82,220); CORAL=(255,101,91); TEAL=(42,197,170); YELLOW=(255,198,56); BLUE=(55,151,255)


def sc(v): return int(round(v*S))
def rgba(c,a=255): return (*c,a)
def font(face,size): return ImageFont.truetype(str(FONT_DIR/face),sc(size))

def text(im,xy,value,size,fill=WHITE,face=F_REG,anchor="rt"):
    return FD(im).text((sc(xy[0]),sc(xy[1])),value,font=font(face,size),fill=fill,anchor=anchor)

def rect(d,box,fill=None,outline=None,width=1,radius=0):
    d.rounded_rectangle(tuple(sc(v) for v in box),radius=sc(radius),fill=fill,outline=outline,width=sc(width) if outline else 1)

def ellipse(d,box,fill=None,outline=None,width=1):
    d.ellipse(tuple(sc(v) for v in box),fill=fill,outline=outline,width=sc(width) if outline else 1)

def line(d,pts,fill,width=2):
    d.line([(sc(x),sc(y)) for x,y in pts],fill=fill,width=sc(width),joint="curve")

def cover_crop(path, target=(W,H), zoom=1.0, focus=(0.5,0.5)):
    im=Image.open(path).convert("RGB")
    tw,th=target; scale=max(tw/im.width,th/im.height)*zoom
    nw,nh=round(im.width*scale),round(im.height*scale)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    fx,fy=focus
    l=max(0,min(nw-tw,round(fx*nw-tw/2)))
    t=max(0,min(nh-th,round(fy*nh-th/2)))
    return im.crop((l,t,l+tw,t+th)).convert("RGBA")

def vertical_gradient(size, stops):
    w,h=size
    grad=Image.new("RGBA",size)
    p=grad.load()
    stops=sorted(stops)
    for y in range(h):
        q=y/(h-1)
        for i in range(len(stops)-1):
            q0,c0=stops[i]; q1,c1=stops[i+1]
            if q0<=q<=q1:
                u=(q-q0)/(q1-q0) if q1>q0 else 0
                c=tuple(round(c0[k]*(1-u)+c1[k]*u) for k in range(4)); break
        else: c=stops[0][1] if q<stops[0][0] else stops[-1][1]
        for x in range(w): p[x,y]=c
    return grad

def topbar(im,page,accent):
    """Minimal page marker; intentionally no category or series name."""
    d=ImageDraw.Draw(im,"RGBA")
    rect(d,(52,42,190,110),fill=rgba(NAVY,178),outline=rgba(WHITE,55),width=1,radius=34)
    ellipse(d,(72,65,94,87),fill=rgba(accent))
    text(im,(116,76),f"{page:02d} / 05",15,WHITE,F_BLACK,"lm")

def dots(im,page):
    d=ImageDraw.Draw(im,"RGBA")
    for i in range(5):
        x=485+i*29
        ellipse(d,(x,1300,x+12,1312),fill=rgba(YELLOW if i==page-1 else WHITE,255 if i==page-1 else 110))

def label(im,x,y,label,color):
    d=ImageDraw.Draw(im,"RGBA")
    w=max(122,24+len(label)*10)
    rect(d,(x-w,y,x,y+42),fill=rgba(color,235),radius=21)
    text(im,(x-17,y+21),label,17,NAVY if color==YELLOW else WHITE,F_BLACK,"rm")

def glass_card(im,box,color=TEAL,alpha=205):
    d=ImageDraw.Draw(im,"RGBA")
    rect(d,box,fill=rgba(NAVY,alpha),outline=rgba(color,190),width=2,radius=26)
    x1,y1,x2,y2=box
    rect(d,(x2-14,y1+22,x2-7,y2-22),fill=rgba(color),radius=4)

def slide1():
    # Dedicated cover art keeps the baby large without previewing any lesson items.
    im=cover_crop(ASSETS/"scene_cover.png",zoom=1.03,focus=(0.50,0.50))
    scr=vertical_gradient((W,H),[(0.0,rgba(NAVY,225)),(0.38,rgba(NAVY,92)),(0.66,rgba(NAVY,0)),(1.0,rgba(NAVY,150))])
    im=Image.alpha_composite(im,scr)
    d=ImageDraw.Draw(im,"RGBA")
    topbar(im,1,YELLOW)
    text(im,(1010,170),"پنج کاری که",68,WHITE,F_BLACK,"rt")
    text(im,(1010,258),"نوزادت را",72,WHITE,F_BLACK,"rt")
    text(im,(1010,350),"«باهوش‌تر» نمی‌کند",78,YELLOW,F_BLACK,"rt")
    rect(d,(778,1168,1010,1238),fill=rgba(CORAL,240),radius=24)
    text(im,(982,1203),"ورق بزن",23,WHITE,F_BLACK,"rm")
    dots(im,1)
    return im

def slide2():
    im=cover_crop(ASSETS/"scene_02.png")
    scr=vertical_gradient((W,H),[(0.0,rgba(NAVY,190)),(0.28,rgba(NAVY,0)),(0.68,rgba(NAVY,10)),(1.0,rgba(NAVY,210))])
    im=Image.alpha_composite(im,scr); d=ImageDraw.Draw(im,"RGBA")
    topbar(im,2,PURPLE); label(im,1004,150,"شماره ۱ و ۲",PURPLE)
    text(im,(1006,220),"گران‌تر و زودتر،",48,WHITE,F_BLACK,"rt")
    text(im,(1006,283),"باهوش‌تر نمی‌کند",54,YELLOW,F_BLACK,"rt")
    glass_card(im,(55,988,1025,1258),PURPLE,228)
    text(im,(972,1025),"اسباب‌بازی گران و فلش‌کارت اجباری",30,YELLOW,F_BLACK,"rt")
    text(im,(972,1085),"میان‌بُر افزایش هوش نیستند.",28,WHITE,F_BLACK,"rt")
    text(im,(972,1148),"بازی ساده با یک بزرگسالِ پاسخ‌گو",25,TEAL,F_BLACK,"rt")
    text(im,(972,1194),"برای رشد، ارزشمندتر است.",25,TEAL,F_BLACK,"rt")
    dots(im,2); return im

def slide3():
    im=cover_crop(ASSETS/"scene_03.png")
    # Original image has a generous cream lower field.
    d=ImageDraw.Draw(im,"RGBA"); topbar(im,3,CORAL); label(im,1004,150,"شماره ۳",CORAL)
    glass_card(im,(56,745,1024,1255),TEAL,230)
    text(im,(970,790),"اپ و ویدئوی",46,WHITE,F_BLACK,"rt")
    text(im,(970,856),"«تقویت مغز نوزاد»؟",51,YELLOW,F_BLACK,"rt")
    line(d,[(560,930),(970,930)],rgba(CORAL),6)
    text(im,(970,970),"صفحه‌نمایش جای تعامل زنده را نمی‌گیرد.",29,WHITE,F_BLACK,"rt")
    text(im,(970,1035),"چهره، صدا و پاسخ واقعی شما",28,TEAL,F_BLACK,"rt")
    text(im,(970,1088),"برای یادگیری مهم‌تر است.",28,TEAL,F_BLACK,"rt")
    rect(d,(565,1150,970,1225),fill=rgba(CORAL,240),radius=20)
    text(im,(940,1187),"تعامل کن، فقط پخش نکن",24,WHITE,F_BLACK,"rm")
    dots(im,3); return im

def slide4():
    im=cover_crop(ASSETS/"scene_04.png")
    scr=vertical_gradient((W,H),[(0.0,rgba(NAVY,205)),(0.27,rgba(NAVY,0)),(0.67,rgba(NAVY,0)),(1.0,rgba(NAVY,220))])
    im=Image.alpha_composite(im,scr); topbar(im,4,YELLOW); label(im,1004,150,"شماره ۴ و ۵",YELLOW)
    text(im,(1006,220),"موسیقی و مکمل؛",48,WHITE,F_BLACK,"rt")
    text(im,(1006,282),"نه میان‌بُرِ IQ",53,CORAL,F_BLACK,"rt")
    glass_card(im,(55,986,1025,1258),YELLOW,230)
    text(im,(972,1025),"موسیقی لذت‌بخش است؛",29,WHITE,F_BLACK,"rt")
    text(im,(972,1078),"اما معجزهٔ هوش نیست.",29,WHITE,F_BLACK,"rt")
    text(im,(972,1136),"مکملِ بدون نیاز پزشکی، هوش را بیشتر نمی‌کند.",25,YELLOW,F_BLACK,"rt")
    text(im,(972,1192),"مکمل فقط طبق توصیهٔ پزشک و شرایط نوزاد.",22,TEAL,F_BLACK,"rt")
    dots(im,4); return im

def slide5():
    im=cover_crop(ASSETS/"scene_05.png")
    scr=vertical_gradient((W,H),[(0.0,rgba(NAVY,205)),(0.32,rgba(NAVY,20)),(0.62,rgba(NAVY,0)),(1.0,rgba(NAVY,225))])
    im=Image.alpha_composite(im,scr); d=ImageDraw.Draw(im,"RGBA")
    topbar(im,5,TEAL); label(im,1004,150,"پس چه چیزی کمک می‌کند؟",TEAL)
    text(im,(1006,220),"رشد مغز از رابطه می‌آید،",43,WHITE,F_BLACK,"rt")
    text(im,(1006,278),"نه از شعار روی جعبه",49,YELLOW,F_BLACK,"rt")
    glass_card(im,(55,1017,1025,1258),TEAL,218)
    items=[("حرف بزن و پاسخ بده",CORAL),("کتاب بخوان و آواز بخوان",YELLOW),("بازی آزاد و امن",TEAL),("خواب، تغذیه و مراقبت پزشکی",BLUE)]
    for i,(s,c) in enumerate(items):
        col=i%2; row=i//2; x=87+col*455; y=1053+row*83
        rect(d,(x,y,x+414,y+62),fill=rgba(WHITE,20),outline=rgba(c,150),width=1,radius=17)
        ellipse(d,(x+22,y+19,x+46,y+43),fill=rgba(c))
        text(im,(x+385,y+31),s,17,WHITE,F_BOLD,"rm")
    text(im,(970,1230),"ذخیره کن و برای یک والد تازه‌کار بفرست.",17,YELLOW,F_BOLD,"rb")
    dots(im,5); return im

def save(im,path):
    im.convert("RGB").resize((1080,1350),Image.Resampling.LANCZOS).save(path,quality=94,optimize=True)

def preview(paths,path):
    tw,th,cols=270,338,3; rows=2
    out=Image.new("RGB",(cols*tw+48,rows*th+48),NAVY); d=ImageDraw.Draw(out)
    for i,p in enumerate(paths):
        im=Image.open(p).convert("RGB").resize((tw,th),Image.Resampling.LANCZOS)
        x=24+(i%cols)*tw; y=24+(i//cols)*th; out.paste(im,(x,y)); d.rectangle((x,y,x+tw-1,y+th-1),outline=TEAL,width=2)
    out.save(path,quality=92,optimize=True)

def main():
    OUT.mkdir(exist_ok=True)
    paths=[]
    for i,im in enumerate([slide1(),slide2(),slide3(),slide4(),slide5()],1):
        p=OUT/f"slide_{i:02d}.jpg"; save(im,p); paths.append(p)
    preview(paths,OUT/"carousel_preview.jpg")
    (OUT/"caption.txt").write_text("""۵ کاری که نوزادت را «باهوش‌تر» نمی‌کند 🧠✨

اسباب‌بازی گران، فلش‌کارت اجباری، اپ‌های موسوم به تقویت مغز، پخش موسیقی کلاسیک و مکمل‌های تبلیغاتی میان‌بُر افزایش هوش نیستند.

آنچه بیشتر کمک می‌کند، تعامل رفت‌وبرگشتی است: به نگاه و صدای نوزاد پاسخ بدهید، با او حرف بزنید، کتاب بخوانید، آواز بخوانید و فرصت بازی آزاد و امن بدهید. خواب، تغذیه و مراقبت‌های معمول پزشکی هم پایه‌های مهم رشدند.

مکمل‌ها را فقط مطابق توصیهٔ پزشک و متناسب با سن و شرایط کودک استفاده کنید.

این محتوا آموزشی است و جایگزین ارزیابی پزشک اطفال نیست.

#رشد_نوزاد #هوش_نوزاد #بازی_با_نوزاد #والدگری #تربیت_کودک #پزشک_اطفال
""",encoding="utf-8")
    (OUT/"README.md").write_text("""# کاروسل مولتی‌کالر سه‌بعدی

- عنوان: ۵ کاری که نوزادت را «باهوش‌تر» نمی‌کند
- ۵ اسلاید ۴:۵ برای پست اینستاگرام
- ابعاد نهایی: ۱۰۸۰×۱۳۵۰
- سبک: تصویرسازی سینمایی سه‌بعدی خانوادگی، مولتی‌کالر
- ترتیب انتشار: `slide_01.jpg` تا `slide_05.jpg`
""",encoding="utf-8")
    print(f"Created {len(paths)} slides")

if __name__=="__main__": main()
