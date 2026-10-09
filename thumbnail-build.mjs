/** Freeze representative photos in their existing bottom positions after the unchanged public pipeline. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';import {spawnSync} from 'node:child_process';
import {parseHTML} from './image-order-build.mjs';
const root=path.dirname(fileURLToPath(import.meta.url)),output=path.join(root,'.public-release'),review=JSON.parse(fs.readFileSync(path.join(root,'thumbnail-review.json'),'utf8'));
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const ancestor=(n,test)=>{for(let p=n.parent;p;p=p.parent)if(test(p))return p;return null};
const hash=b=>createHash('sha256').update(b).digest('hex');
function edit(s,edits){edits.sort((a,b)=>b.start-a.start||b.end-a.end);let previous=s.length+1;for(const e of edits){if(e.end>previous)throw Error('Overlapping photo edits');s=s.slice(0,e.start)+e.value+s.slice(e.end);previous=e.start}return s}
function absolute(src,name){return new URL(src,'https://'+review.host+'/'+name).href}
function imageFields(n,p){const photo=p.selected,url=absolute(photo.url,p.name),label=p.center+' '+photo.label;return {...n,name:label,url,contentUrl:url,width:photo.width,height:photo.height,...(n.caption?{caption:label}:{}),...(n.description?{description:label}:{})}}
export function applyPhotoHTML(source,name,p){
 if(source.includes('data-thumbnail-bottom="20261010"'))return {html:source,unchanged:true};
 const nodes=parseHTML(source),main=nodes.find(n=>n.tag==='main');if(!main)throw Error('No main for reviewed photo page '+name);
 const canon=nodes.find(n=>n.tag==='link'&&n.attrs.rel==='canonical')?.attrs.href;if(canon!==p.url)throw Error('Canonical changed '+name);
 const label=p.center+' '+p.selected.label,url=absolute(p.selected.url,name);
 const hidden=nodes.filter(n=>n.tag==='img'&&n.attrs['data-media-role']==='representative'&&(n.attrs.hidden!==undefined||n.attrs['aria-hidden']==='true'||/display\s*:\s*none/i.test(n.attrs.style||'')));
 const edits=hidden.map(n=>({start:n.start,end:n.end,value:''}));
 const selected=nodes.filter(n=>n.tag==='img'&&ancestor(n,x=>x.tag==='main')&&absolute(n.attrs.src,name)===url);
 if(p.operation==='reuse_bottom'){
  if(selected.length!==1)throw Error('Existing bottom photo missing or repeated '+name);
  const im=selected[0];if(!ancestor(im,x=>x.tag==='figure'))throw Error('Photo no longer in its original figure '+name);
  if(im.attrs.hidden!==undefined||ancestor(im,x=>x.tag==='details'&&!('open' in x.attrs)))throw Error('Existing photo is gated '+name);
 }else{
  if(p.operation!=='add_bottom'||selected.length)throw Error('Unreviewed bottom insertion '+name);
  const photo=p.selected;
  const figure='<figure class="crawl-registered-photo" data-thumbnail-photo="20261010"><a class="media-zoom-link" data-media-zoom data-full-width="'+photo.width+'" data-image-y="0" href="'+esc(photo.url)+'" aria-label="'+esc(label+' 원본 확대')+'"><img data-media-role="space" src="'+esc(photo.url)+'" alt="'+esc(label)+'" width="'+photo.width+'" height="'+photo.height+'" style="display:block; width:100%; height:auto; max-width:'+photo.width+'px; aspect-ratio:'+photo.width+' / '+photo.height+';" loading="lazy" decoding="async"></a><figcaption class="crawl-media-caption">'+esc(label)+' · 제공 사진입니다. 촬영 당시의 모습이며 현재 배치는 지점에 확인해 주세요.</figcaption></figure>';
  edits.push({start:main.closeStart,end:main.closeStart,value:figure});
 }
 // Only image-family head tags are normalized; title, description, canonical and favicon remain byte-for-byte.
 const head=nodes.find(n=>n.tag==='head');if(!head)throw Error('No head');
 for(const n of nodes.filter(n=>n.tag==='meta'&&n.start<head.closeStart&&/^(?:og:image(?::.*)?|twitter:image(?::.*)?)$/i.test(n.attrs.property||n.attrs.name||'')))edits.push({start:n.start,end:n.end,value:''});
 const type={JPEG:'image/jpeg',PNG:'image/png',WEBP:'image/webp',GIF:'image/gif'}[p.selected.format];if(!type)throw Error('Unreviewed image format');
 let metadata='<meta property="og:image" content="'+esc(url)+'"><meta property="og:image:secure_url" content="'+esc(url)+'"><meta property="og:image:width" content="'+p.selected.width+'"><meta property="og:image:height" content="'+p.selected.height+'"><meta property="og:image:type" content="'+type+'"><meta property="og:image:alt" content="'+esc(label)+'"><meta name="twitter:image" content="'+esc(url)+'"><meta name="twitter:image:alt" content="'+esc(label)+'">';
 if(p.operation==='add_bottom'&&!source.includes('href="'+review.css+'"'))metadata+='<link rel="stylesheet" href="'+review.css+'">';
 if(p.operation==='add_bottom'&&!source.includes('src="'+review.js+'"'))metadata+='<script defer src="'+review.js+'"></script>';
 edits.push({start:head.closeStart,end:head.closeStart,value:metadata});
 for(const n of nodes.filter(n=>n.tag==='script'&&n.attrs.type==='application/ld+json')){
  const raw=source.slice(n.start,n.end),j=JSON.parse(raw.replace(/^<script\b[^>]*>/i,'').replace(/<\/script>$/i,'')),graph=j['@graph']||[j];
  const pageNodes=graph.filter(x=>[x['@type']].flat().some(t=>['WebPage','Article','CollectionPage'].includes(t))&&x.url===p.url);
  const primaryIDs=new Set(pageNodes.map(x=>x.primaryImageOfPage?.['@id']).filter(Boolean));let changed=false;
  for(let i=0;i<graph.length;i++){
   const x=graph[i];
   if(x['@type']==='ImageObject'&&primaryIDs.has(x['@id'])){graph[i]=imageFields(x,{...p,name});changed=true;continue}
   if(pageNodes.includes(x)){
    if(x.image){x.image=url;changed=true}
    if(x.primaryImageOfPage&&!x.primaryImageOfPage['@id']){x.primaryImageOfPage=typeof x.primaryImageOfPage==='string'?url:imageFields(x.primaryImageOfPage,{...p,name});changed=true}
    if(x.dateModified){x.dateModified=review.date;changed=true}
   }
   if([x['@type']].flat().some(t=>['LocalBusiness','EducationalOrganization'].includes(t))&&x.name===p.center&&x.image){x.image=url;changed=true}
  }
  if(changed){const json=j['@graph']?{...j,'@graph':graph}:graph[0];edits.push({start:n.start,end:n.end,value:raw.replace(/(<script\b[^>]*>)[\s\S]*(<\/script>)$/i,(_,open,close)=>open+JSON.stringify(json)+close)})}
 }
 let html=edit(source,edits);html=html.replace('<main','<main data-thumbnail-bottom="20261010"');
 return {html,removedHidden:hidden.length,added:p.operation==='add_bottom',reused:p.operation==='reuse_bottom'};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(!process.argv.includes('--apply-only')){const r=spawnSync(process.execPath,['favicon-build.mjs'],{cwd:root,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status??1)}
 for(const [u,h] of Object.entries(review.assets)){if(hash(fs.readFileSync(path.join(root,u)))!==h||hash(fs.readFileSync(path.join(output,u)))!==h)throw Error('Photo asset integrity '+u)}
 const records=[],names=Object.keys(review.pages);let index=0;
 await Promise.all(Array.from({length:12},async()=>{while(index<names.length){const name=names[index++],p=review.pages[name],file=path.join(output,name),before=await fs.promises.readFile(file,'utf8'),r=applyPhotoHTML(before,name,p);if(!r.unchanged)await fs.promises.writeFile(file,r.html);records.push({name,...r,html:undefined})}}));
 const paths=new Set(Object.values(review.pages).map(p=>new URL(p.url).pathname));const sitemap=path.join(output,'sitemap.xml');let xml=fs.readFileSync(sitemap,'utf8');
 xml=xml.replace(/<url>[\s\S]*?<\/url>/g,entry=>{const loc=entry.match(/<loc>([^<]+)<\/loc>/)?.[1];if(!loc||!paths.has(new URL(loc).pathname))return entry;return /<lastmod>/.test(entry)?entry.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+review.date+'</lastmod>'):entry.replace('</loc>','</loc><lastmod>'+review.date+'</lastmod>')});fs.writeFileSync(sitemap,xml);
 console.log(JSON.stringify({thumbnailPages:records.length,reusedBottom:records.filter(p=>p.reused).length,addedBottom:records.filter(p=>p.added).length,removedHiddenElements:records.reduce((n,p)=>n+(p.removedHidden||0),0),randomSelection:false,upperPhotoAdded:false}));
}
