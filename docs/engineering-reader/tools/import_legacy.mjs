// One-time conversion. Existing HTML is never overwritten.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {decorate} from './decorate.mjs';
const require=createRequire(process.env.RENEGADE_READER_DEPS || import.meta.url);
const MarkdownIt=require('markdown-it');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const manifest=JSON.parse(fs.readFileSync(new URL('../report-manifest.json',import.meta.url)));
const imported=new Set(manifest.imports);
const htmlEsc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
for(const name of imported){
 const src=path.join(root,name), out=src.replace(/\.md$/,'.html');
 if(fs.existsSync(out))continue;
 let text=fs.readFileSync(src,'utf8').replace(/^---\n[\s\S]*?\n---\n/,'');
 // Preserve TeX before the Markdown parser consumes backslashes/underscores.
 const maths=[];
 text=text.replace(/\$([^$\n]+)\$/g,(_,m)=>{const i=maths.push(m)-1;return `MATHPLACEHOLDER${i}END`;});
 let body=new MarkdownIt({html:false,linkify:false}).render(text);
 body=body.replace(/MATHPLACEHOLDER(\d+)END/g,(_,i)=>`<span class="math">\\(${htmlEsc(maths[+i])}\\)</span>`);
 body=body.replace(/href="([^"]+)"/g,(all,href)=>{
  if(/^(https?:|#)/.test(href))return all;
  const [p,hash]=href.split('#');const abs=path.resolve(path.dirname(src),decodeURIComponent(p));
  const rel=path.relative(root,abs);
  if(imported.has(rel)||rel==='docs/design-journal/calculations/current-power-packaging.md')return `href="${p.replace(/\.md$/,'.html')}${hash?'#'+hash:''}"`;
  return all;
 });
 const title=(text.match(/^# (.+)/m)||[])[1]||path.basename(name);
 fs.writeFileSync(out,`<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><title>${htmlEsc(title)}</title></head><body><main><p class="eyebrow">Renegade · Reviewed engineering record · 26 November 2026</p>${body}</main></body></html>\n`);
 decorate(out);
 console.log(path.relative(root,out));
}
