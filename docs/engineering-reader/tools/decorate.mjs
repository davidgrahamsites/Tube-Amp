// Add local presentation to editable HTML; do not change engineering content.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const home=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const terms=JSON.parse(fs.readFileSync(path.join(home,'vocabulary.json'),'utf8'));
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
export function decorate(file){
 let html=fs.readFileSync(file,'utf8');
 const rel=p=>path.relative(path.dirname(path.resolve(file)),path.join(home,p)).split(path.sep).join('/');
 html=html.replace(/<!-- reader-head -->[\s\S]*?<!-- \/reader-head -->/g,'').replace(/<!-- reader-nav -->[\s\S]*?<!-- \/reader-nav -->/g,'').replace(/<!-- reader-key -->[\s\S]*?<!-- \/reader-key -->/g,'');
 const head=`<!-- reader-head --><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="${rel('assets/reader.css')}"><link rel="stylesheet" href="${rel('assets/katex/katex.min.css')}"><script defer src="${rel('assets/katex/katex.min.js')}"></script><script defer src="${rel('assets/katex/auto-render.min.js')}"></script><script defer src="${rel('assets/math.js')}"></script><!-- /reader-head -->`;
 html=html.replace('</head>',head+'</head>');
 html=html.replace(/<body[^>]*>/,m=>m+`<!-- reader-nav --><header><nav aria-label="Documents"><a href="${rel('index.html')}">Engineering status</a><a href="${rel('glossary.html')}">Vocabulary key</a><a href="${rel('document-standard.html')}">Document standard</a></nav></header><!-- /reader-nav -->`);
 if(!html.includes('<main'))html=html.replace('<!-- /reader-nav -->','<!-- /reader-nav --><main>').replace('</body>','</main></body>');
 if(!file.endsWith('glossary.html')){
  const plain=html.replace(/<[^>]*>/g,' ').toLowerCase();
  const used=Object.entries(terms).filter(([k])=>new RegExp('\\b'+k.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\b','i').test(plain));
  const key=`<!-- reader-key --><section aria-label="Report vocabulary"><h2>Vocabulary key</h2><p>Terms used in this report. See the <a href="${rel('glossary.html')}">full key</a> for related terms.</p><dl>${used.map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('\n')}</dl></section><!-- /reader-key -->`;
  html=html.replace('</main>',key+'</main>');
 }
 fs.writeFileSync(file,html);
}
if(process.argv[1]===fileURLToPath(import.meta.url))for(const p of process.argv.slice(2))decorate(p);
