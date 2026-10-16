/** Append reviewed branch directions; keep all existing URLs, images, text and links. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {parseHTML} from './image-order-build.mjs';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,'.public-release');
const read=()=>JSON.parse(fs.readFileSync(path.join(root,'kakao-directions-review.json'),'utf8'));
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const route=n=>n==='index.html'?'/':'/'+n.replace(/index\.html$/,'');
function edits(s,changes){changes.sort((a,b)=>b.start-a.start);let last=s.length+1;for(const c of changes){if(c.end>last)throw Error('Overlapping map edits');s=s.slice(0,c.start)+c.html+s.slice(c.end);last=c.start;}return s;}
function section(p,m){
 const frame='<iframe class="kakao-map-frame" style="display:block;width:100%;height:392px;border:0" title="'+esc(p.branch)+' 카카오맵" data-kakao-src="'+m.frame+'" data-map-key="'+m.key+'" width="640" height="392" loading="lazy" sandbox="allow-scripts" referrerpolicy="strict-origin-when-cross-origin"></iframe>';
 const fallback='<noscript><iframe class="kakao-map-frame" style="display:block;width:100%;height:392px;border:0" title="'+esc(p.branch)+' 카카오맵" src="'+m.frame+'" width="640" height="392" loading="lazy" sandbox="allow-scripts" referrerpolicy="strict-origin-when-cross-origin"></iframe></noscript>';
 return '<section class="kakao-directions" id="kakao-directions" aria-labelledby="kakao-directions-title" data-kakao-branch="'+esc(p.branch)+'"><h2 id="kakao-directions-title">찾아오시는 길</h2><p>'+esc(p.branch)+'의 위치와 주변 교통편을 확인하세요.</p><div class="kakao-map-slot">'+frame+'<p class="kakao-map-loading" aria-hidden="true">지도를 불러오는 중입니다.</p>'+fallback+'</div><dl class="kakao-address"><dt>주소</dt><dd>'+esc(p.address)+'</dd></dl>'+m.transitHTML+'<p class="kakao-transit-note">주변 교통정보는 카카오맵 약도의 안내를 기준으로 정리했습니다. 버스 노선과 운행 상황은 이동 전에 확인해 주세요.</p></section>';
}
export function improveMaps(source,name,review){
 const p=review.pages[name],hub=review.hubs.includes(name);if(!p&&!hub)return {html:source,changed:false};
 if(source.includes('id="kakao-directions"')||source.includes('data-kakao-hub-link'))return {html:source,changed:false};
 const ns=parseHTML(source),main=ns.find(n=>n.tag==='main');if(!main)throw Error('Map target has no main '+name);
 const changes=[],counts={};
 if(p){
  const maps=ns.filter(n=>n.tag==='img'&&n.attrs['data-media-role']==='map');if(maps.length>1)throw Error('Ambiguous existing map '+name);
  let where;
  if(maps.length){let f=maps[0].parent;while(f&&f.tag!=='figure')f=f.parent;if(!f)throw Error('Map image lacks figure '+name);where=f.end;counts.belowExistingMap=1;}
  else{
   const sequence=ns.find(n=>n.attrs['data-image-order']==='sequence-v1'),info=ns.find(n=>n.attrs.id==='branch-information');
   if(sequence)where=sequence.end;else if(info)where=info.end;else throw Error('No reviewed insertion location '+name);
   counts.withoutExistingMap=1;
  }
  changes.push({start:where,end:where,html:section(p,review.maps[p.branch])});counts.detailPages=1;
 }else{
  for(const card of ns.filter(n=>n.tag==='article'&&(Object.hasOwn(n.attrs,'data-center-card')||Object.hasOwn(n.attrs,'data-teacher-branch')))){
   const links=ns.filter(n=>n.tag==='a'&&n.start>card.start&&n.end<card.end&&n.attrs.href);
   const target=links.map(n=>({node:n,name:decodeURIComponent(new URL(n.attrs.href,'https://'+review.host).pathname).slice(1)+'index.html'})).find(x=>review.pages[x.name]);
   if(!target)continue;
   const branch=review.pages[target.name].branch;
   changes.push({start:card.closeStart,end:card.closeStart,html:'<a class="kakao-hub-link" data-kakao-hub-link href="'+esc(target.node.attrs.href.split('#')[0])+'#kakao-directions">'+esc(branch)+' 위치·교통정보</a>'});counts.hubLinks=(counts.hubLinks||0)+1;
  }
  if(!changes.length)throw Error('Hub map links not found '+name);counts.hubs=1;
 }
 let s=edits(source,changes);s=s.replace('</head>','<link rel="stylesheet" href="'+review.css+'" media="print" onload="this.media=\'all\';this.onload=null"><noscript><link rel="stylesheet" href="'+review.css+'"></noscript>'+(p?'<script defer src="'+review.js+'"></script>':'')+'</head>');
 s=s.replace(/(<script\b[^>]*type="application\/ld\+json"[^>]*>)([\s\S]*?)(<\/script>)/g,(raw,open,json,close)=>{
  const data=JSON.parse(json);let modified=false;for(const x of data['@graph']||[data])if(['WebPage','Article','CollectionPage','ContactPage'].includes(x['@type'])&&x.dateModified){x.dateModified=review.date;modified=true;}return modified?open+JSON.stringify(data)+close:raw;
 });
 return {html:s,changed:true,counts};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const review=read();
 if(!process.argv.includes('--apply-only')){const r=spawnSync(process.execPath,['discovery-build.mjs'],{cwd:root,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status??1);}
 const files=Object.keys(review.pages).concat(review.hubs),changed=[],counts={};let cursor=0;
 await Promise.all(Array.from({length:12},async()=>{while(cursor<files.length){const name=files[cursor++],file=path.join(out,name),s=await fs.promises.readFile(file,'utf8'),r=improveMaps(s,name,review);if(r.changed){await fs.promises.writeFile(file,r.html);changed.push(route(name));for(const [k,v] of Object.entries(r.counts))counts[k]=(counts[k]||0)+v;}}}));
 const paths=new Set(changed),sitemap=path.join(out,'sitemap.xml');let xml=fs.readFileSync(sitemap,'utf8');xml=xml.replace(/<url>[\s\S]*?<\/url>/g,entry=>{const loc=entry.match(/<loc>([^<]+)<\/loc>/)?.[1];if(!loc||!paths.has(decodeURIComponent(new URL(loc).pathname)))return entry;return entry.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+review.date+'</lastmod>');});fs.writeFileSync(sitemap,xml);
 console.log(JSON.stringify({kakaoDirectionsPages:changed.length,counts,maps:Object.keys(review.maps).length,originalImagesAndLinksPreserved:true}));
}
