import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL,fileURLToPath} from 'node:url';
import os from 'node:os';
const require=createRequire(process.env.RENEGADE_READER_DEPS || import.meta.url);const {chromium}=require('playwright');
const home=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'renegade-equipment-'));const isolated=path.join(scratch,'test-equipment.html');fs.copyFileSync(path.join(home,'exports/test-equipment.html'),isolated);
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const ctx=await browser.newContext({offline:true});const page=await ctx.newPage();let errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure()?.errorText));
let checks=[];
for(const width of [1280,390]){
 await page.setViewportSize({width,height:900});await page.goto(pathToFileURL(isolated).href);await page.waitForFunction(()=>document.documentElement.dataset.mathReady==='true');await page.evaluate(()=>document.fonts.ready);
 const state=await page.evaluate(()=>({title:document.title,equations:document.querySelectorAll('.katex').length,mathErrors:window.readerMathErrors,overflow:document.documentElement.scrollWidth>innerWidth+1,externalAssets:[...document.querySelectorAll('script[src],link[rel="stylesheet"],img[src]')].length,missingAnchors:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash)}));
 checks.push({width,...state});await page.screenshot({path:path.join(home,`evidence/equipment-${width}.png`)});
 if(width===1280){await page.locator('#records').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(home,'evidence/equipment-math.png')});}
}
await browser.close();fs.rmSync(scratch,{recursive:true});const passed=checks.every(c=>c.equations>=8&&!c.mathErrors.length&&!c.overflow&&!c.externalAssets&&!c.missingAnchors.length)&&!errors.length;
fs.writeFileSync(path.join(home,'evidence/equipment-checks.json'),JSON.stringify({date:'2026-11-26',offline:true,isolatedCopy:true,checks,errors,passed,hardwareTested:false},null,2)+'\n');console.log(JSON.stringify({checks,errors,passed},null,2));if(!passed)process.exitCode=1;
