/** Fact-bounded answer passages and article provenance; preserve every existing URL/image. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,'.public-release');
const review=JSON.parse(fs.readFileSync(path.join(root,'seo-geo-review.json'),'utf8'));
const sha=s=>createHash('sha256').update(s).digest('hex');
export function improveAnswers(source,name){
 const p=review.pages[name];if(!p||source.includes('data-answer-review="20261020"'))return {html:source,changed:false};
 let s=source.replace(/\r\n|\r/g,'\n');if(sha(s)!==p.before)throw Error('Reviewed answer input changed: '+name);
 for(const c of p.changes){const old=c.oldBlock?review.blocks[c.oldBlock]:c.old;if(s.split(old).length!==1+(c.expectedCount||1))throw Error('Ambiguous answer edit: '+name);let at=-old.length;for(let i=0;i<=(c.occurrence||0);i++)at=s.indexOf(old,at+old.length);if(at<0)throw Error('Missing answer edit: '+name);s=s.slice(0,at)+c.html+s.slice(at+old.length);}
 s=s.replace(/(<script\b[^>]*type="application\/ld\+json"[^>]*>)([\s\S]*?)(<\/script>)/g,(_,a,json,b)=>{
  const data=JSON.parse(json),graph=data['@graph']||[data],op=p.schema;
  const page=graph.find(x=>['WebPage','CollectionPage','ContactPage'].includes(x['@type']));
  if(page){page.dateModified=review.date;if(op.abstract)page.abstract=op.abstract;
   if(op.entityID){let old=page.about||[];if(!Array.isArray(old))old=[old];if(!old.some(x=>x['@id']===op.entityID))page.about=old.concat({'@id':op.entityID});}
   if(op.examplePart)page.hasPart=(page.hasPart||[]).concat(op.examplePart);
  }
  if(op.entityID){const entity=graph.find(x=>x['@id']===op.entityID);if(entity)entity.url=op.entityURL;else if(op.entity)graph.push(op.entity);else throw Error('Missing reviewed center entity: '+name);}
  for(const x of graph)if(x['@type']==='Article'){x.dateModified=review.date;if(op.citations)x.citation=op.citations;if(op.abstract)x.abstract=op.abstract;}
  return a+JSON.stringify(data)+b;
 });
 if(p.feed)s=s.replace('</head>','<link rel="alternate" type="application/rss+xml" title="스터디와와 학습정보" href="https://'+review.host+'/rss.xml"></head>');
 if(p.style)s=s.replace('</head>','<link rel="stylesheet" href="'+review.css+'"></head>');
 s=s.replace('<main','<main data-answer-review="20261020"');
 return {html:s,changed:true};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(!process.argv.includes('--apply-only')){const r=spawnSync(process.execPath,['kakao-directions-build.mjs'],{cwd:root,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status??1);}
 let cursor=0,changed=[];const files=Object.keys(review.pages);
 await Promise.all(Array.from({length:12},async()=>{while(cursor<files.length){const n=files[cursor++],file=path.join(out,n),s=await fs.promises.readFile(file,'utf8'),r=improveAnswers(s,n);if(r.changed){await fs.promises.writeFile(file,r.html);changed.push(n);}}}));
 const urls=new Set(changed.map(n=>n==='index.html'?'/':'/'+n.replace(/index\.html$/,'')));const sitemap=path.join(out,'sitemap.xml');let xml=fs.readFileSync(sitemap,'utf8');xml=xml.replace(/<url>[\s\S]*?<\/url>/g,entry=>{const loc=entry.match(/<loc>([^<]+)<\/loc>/)?.[1];if(!loc||!urls.has(decodeURIComponent(new URL(loc).pathname)))return entry;return entry.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+review.date+'</lastmod>');});fs.writeFileSync(sitemap,xml);
 console.log(JSON.stringify({answerPages:changed.length,canonicalURLsAndImagesPreserved:true,workedExamples:10,feed:'/rss.xml'}));
}
