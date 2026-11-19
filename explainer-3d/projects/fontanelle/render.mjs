import {chromium} from 'playwright';
import chromiumBinary from '@sparticuz/chromium';
import {createServer} from 'node:http';
import {readFile, stat} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../..');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.ttf':'font/ttf','.png':'image/png'};
const server=createServer(async(req,res)=>{try{const p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!p.startsWith(root+path.sep))throw Error('invalid path');const f=(await stat(p)).isDirectory()?path.join(p,'index.html'):p;res.setHeader('Content-Type',types[path.extname(f)]||'application/octet-stream');res.end(await readFile(f))}catch{res.statusCode=404;res.end('Not found')}});
server.listen(0,'127.0.0.1');await once(server,'listening');const port=server.address().port;const url=`http://127.0.0.1:${port}/explainer-3d/projects/fontanelle/index.html`;
let browser;try {
 browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||await chromiumBinary.executablePath(),args:[...chromiumBinary.args,'--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'],headless:true});
 const p=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
 for (const [name,w,h] of [['cover_4x5.png',1080,1350],['cover_9x16.png',1080,1920]]) {await p.setViewportSize({width:w,height:h});await p.goto(url+'?cover=1',{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:path.join(dir,name)});console.log('Created '+name)}
 if(process.env.COVER_ONLY!=='1'){
 await p.setViewportSize({width:1920,height:1080});p.on('pageerror',e=>console.error('Page error:',e));await p.goto(url+'?render=1',{waitUntil:'networkidle'});await p.waitForFunction(()=>typeof window.renderAtTime==='function');await p.evaluate(()=>document.fonts.ready);
 const ff=process.env.FFMPEG||'ffmpeg', audio=path.join(dir,'voiceover.mp3');let args=['-y','-f','image2pipe','-framerate','60','-vcodec','mjpeg','-i','pipe:0'];if(existsSync(audio))args.push('-i',audio,'-map','0:v','-map','1:a','-af','apad','-c:a','aac');else args.push('-an');args.push('-t','25','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-r','60','-movflags','+faststart',path.join(dir,'output.mp4'));
 const proc=spawn(ff,args,{stdio:['pipe','ignore','inherit']});let error;proc.on('error',e=>error=e);proc.stdin.on('error',e=>error=e);const closed=once(proc,'close');for(let i=0;i<1500;i++){if(error)throw error;await p.evaluate(t=>window.renderAtTime(t),i/60);const buf=await p.screenshot({type:'jpeg',quality:88});if(!proc.stdin.write(buf))await once(proc.stdin,'drain');if(i%60===0)console.log(`Frame ${i}/1500`)}proc.stdin.end();const [code]=await closed;if(code!==0)throw Error(`ffmpeg exited ${code}`);await p.close();console.log('Done: output.mp4');}
}finally{if(browser)await browser.close();server.close()}
