import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const require=createRequire(process.env.RENEGADE_READER_DEPS || import.meta.url);
const {chromium}=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const home=path.join(root,'docs/engineering-reader');
const manifest=JSON.parse(fs.readFileSync(path.join(home,'report-manifest.json')));
const pages=[...manifest.imports.map(p=>p.replace(/\.md$/,'.html')),...manifest.authored];
const failures=[],results=[];
const browser=await chromium.launch({headless:true,executablePath:process.env.RENEGADE_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const context=await browser.newContext({viewport:{width:1280,height:900},offline:true});
const page=await context.newPage();
for(const rel of pages){
 const errors=[];const listener=err=>errors.push(String(err));page.on('pageerror',listener);
 await page.goto(pathToFileURL(path.join(root,rel)).href);
 await page.waitForFunction(()=>document.documentElement.dataset.mathReady==='true');
 await page.evaluate(()=>document.fonts.ready);
 const state=await page.evaluate(()=>({title:document.title,equations:document.querySelectorAll('.katex').length,mathErrors:window.readerMathErrors,overflow:document.documentElement.scrollWidth>innerWidth+1,links:[...document.querySelectorAll('a[href],link[href],script[src]')].map(x=>x.href||x.src)}));
 for(const url of state.links){if(url.startsWith('file:')){const u=new URL(url);u.hash='';if(!fs.existsSync(fileURLToPath(u)))errors.push('Missing local link: '+url);}}
 if(state.mathErrors.length||state.overflow||errors.length)failures.push({rel,...state,errors});
 results.push({file:rel,equations:state.equations,pageErrors:errors,mathErrors:state.mathErrors,horizontalOverflow:state.overflow});
 page.off('pageerror',listener);
}
const math='docs/design-journal/calculations/current-power-packaging.html';
await page.goto(pathToFileURL(path.join(root,math)).href);await page.waitForFunction(()=>document.documentElement.dataset.mathReady==='true');await page.evaluate(()=>document.fonts.ready);
await page.screenshot({path:path.join(home,'evidence/calculations-desktop.png')});
await page.setViewportSize({width:390,height:844});
const mobile=await page.evaluate(()=>({pageOverflow:document.documentElement.scrollWidth>innerWidth+1,mathErrors:window.readerMathErrors}));
if(mobile.pageOverflow||mobile.mathErrors.length)failures.push({mobile});
await page.screenshot({path:path.join(home,'evidence/calculations-mobile.png')});
await page.setViewportSize({width:1280,height:900});await page.goto(pathToFileURL(path.join(home,'index.html')).href);await page.waitForFunction(()=>document.documentElement.dataset.mathReady==='true');
await page.screenshot({path:path.join(home,'evidence/status-desktop.png')});
await browser.close();
fs.writeFileSync(path.join(home,'evidence/reader-checks.json'),JSON.stringify({date:new Date().toISOString().slice(0,10),offline:true,hardwareVerified:false,pages:results,mobile,passed:failures.length===0,failures},null,2)+'\n');
console.log(JSON.stringify({pages:results.length,equations:results.reduce((n,x)=>n+x.equations,0),mobile,failures},null,2));
if(failures.length)process.exitCode=1;
