/** Enhance only reviewed public media and fact-bound local guidance after the media-order pass. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseHTML,targetPage} from './image-order-build.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const plain=s=>s.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
const decode=s=>s.replaceAll('&amp;','&');
const routeOf=name=>name==='index.html'?'/':'/'+name.replace(/index\.html$/,'');
const imagePath=(src,name)=>decodeURIComponent(new URL(decode(src),'https://xn--2z1b50xixca111l.com'+routeOf(name)).pathname);
const attribute=(tag,key,value)=>{const re=new RegExp('\\s'+key+'(?:\\s*=\\s*(?:"[^"]*"|\'[^\']*\'|[^\\s>]+))?','i');return re.test(tag)?tag.replace(re,' '+key+'="'+esc(value)+'"'):tag.replace(/\s*\/?>$/,' '+key+'="'+esc(value)+'">')};
const ancestor=(n,tag)=>{for(let p=n.parent;p;p=p.parent)if(p.tag===tag)return p;return null};
const replaceSpans=(s,edits)=>{edits.sort((a,b)=>b.start-a.start||b.end-a.end);let last=s.length+1;for(const e of edits){if(e.end>last)throw Error('Overlapping HTML changes');s=s.slice(0,e.start)+e.html+s.slice(e.end);last=e.start}return s};
const safeOriginal=src=>{if(!src.startsWith('/assets/'))throw Error('Unreviewed original image');return src};
const reserveSections=s=>s.replace(/<img\b[^>]*data-media-piece="\d+"[^>]*>/g,tag=>{const w=tag.match(/\bwidth="(\d+)"/)?.[1],h=tag.match(/\bheight="(\d+)"/)?.[1];return attribute(tag,'style','aspect-ratio: '+w+' / '+h+';')});
function registeredPhoto(source,name,review){
 if(source.includes('data-registered-photo='))return source;
 const parts=name.split('/');let selected;
 if(parts[0]==='선생님찾기'&&parts.length===3)selected=review.photos?.[parts[1]];
 if(parts[0]==='전국학원'&&parts[1]==='와와학습코칭센터'&&parts.length===4&&!source.includes('id="center-visit"')){const row=review.locals[parts[2]];if(row)selected=Object.values(review.photos||{}).find(p=>p.center===row['센터명']&&p.address===row['센터 주소']);}
 if(!selected)return source;
 const variants=selected.variants||[];const display=variants[0]?.url||selected.url;const srcset=variants.length?' srcset="'+variants.map(v=>esc(v.url)+' '+v.width+'w').join(', ')+'" sizes="(max-width: 640px) calc(100vw - 80px), (max-width: 1000px) calc(100vw - 100px), 918px"':'';
 const figure='<figure class="crawl-registered-photo" data-registered-photo="'+selected.id+'"><a class="media-zoom-link" data-media-zoom data-full-width="'+selected.width+'" data-image-y="0" href="'+esc(selected.url)+'" aria-label="'+esc(selected.center+' 등록 사진 원본 확대')+'"><img data-media-role="space" src="'+esc(display)+'"'+srcset+' alt="'+esc(selected.center+' 제공 지점 등록 사진')+'" width="'+selected.width+'" height="'+selected.height+'" style="aspect-ratio: '+selected.width+' / '+selected.height+'; max-width: '+selected.width+'px;" loading="lazy" decoding="async"></a><figcaption class="crawl-media-caption">'+esc(selected.center)+' · 제공 자료에 등록된 지점 사진입니다. 촬영 시점과 현재 배치·수업 운영은 방문 전에 확인해 주세요.</figcaption></figure>';
 return source.replace('</main>',figure+'</main>');
}
function schoolTable(row){
 const choices=[['elementary','초등','학교 학습지·사용 교과서','최근 단원에서 혼자 설명한 문제와 도움받은 문제를 구분하고, 풀이·읽기 흔적을 가져옵니다.','학교 과제와 집에서 복습할 분량을 나누고, 다음 점검에서 스스로 설명할 내용을 정합니다.'],['middle','중등','시험 범위표·수업 프린트·수행평가 안내','시험 범위의 단원과 프린트 페이지를 표시하고, 개념·계산·서술 중 막힌 단계를 적습니다.','학교 진도와 현재 이해를 대조해 먼저 복습할 부분을 고르고, 수행평가 마감일도 일정에 표시합니다.'],['high','고등','정확한 과목명·교과서·평가 범위와 방식','공통·선택 과목명을 확인하고, 풀다 멈춘 지점과 조건을 놓친 풀이를 함께 가져옵니다.','과목별 평가 안내와 현재 풀이를 비교해 보완할 개념을 정합니다. 선택과목 수업 개설 여부는 별도로 문의합니다.']];
 const rows=choices.filter(([k])=>row.schools?.[k]?.length).map(([k,label,material,record,next])=>'<tr><td data-label="학교급">'+label+'</td><td data-label="가져올 자료">'+material+'</td><td data-label="학생이 표시할 내용">'+record+'</td><td data-label="상담에서 정할 내용">'+next+'</td></tr>').join('');
 return rows?'<table class="crawl-school-table"><caption>학교 자료를 학습 계획으로 연결하는 순서</caption><thead><tr><th scope="col">학교급</th><th scope="col">가져올 자료</th><th scope="col">학생이 표시할 내용</th><th scope="col">상담에서 정할 내용</th></tr></thead><tbody>'+rows+'</tbody></table>':'';
}
export function enhanceHTML(source,name,review){
 if(source.includes('data-crawl-enhanced="20261007"')){const repaired=registeredPhoto(reserveSections(source),name,review).replace(/<link rel="stylesheet" href="\/assets\/crawl-media-[a-f0-9]+\.css">/g,'<link rel="stylesheet" href="'+review.css+'">').replace(/<script defer src="\/assets\/crawl-media-[a-f0-9]+\.js"><\/script>/g,'<script defer src="'+review.js+'"></script>');return {html:repaired,changed:repaired!==source,counts:{reservedRatios:Number(repaired!==source)}};}
 let s=source;const nodes=parseHTML(s),edits=[];const main=nodes.find(n=>n.tag==='main');if(!main)return {html:s,changed:false};
 const h1=nodes.find(n=>n.tag==='h1'),label=h1?plain(s.slice(h1.openEnd,h1.closeStart)):'';const parts=name.split('/'),row=review.locals[parts[2]];const counts={segments:0,maps:0,teacherFacts:0,schoolTables:0,regions:0,png:0};
 if(targetPage(name)){
  const images=nodes.filter(n=>n.tag==='img'&&ancestor(n,'main'));
  for(const im of images){
   const role=im.attrs['data-media-role'];if(!['body','map'].includes(role))continue;
   const src=safeOriginal(imagePath(im.attrs.src,name));const picture=ancestor(im,'picture');const block=picture??im;
   if(ancestor(block,'a'))throw Error('Existing zoom link requires review: '+name);
   if(role==='body'&&review.media[src]){
    const media=review.media[src];let html='<div class="guide-sections" data-media-source="'+esc(src)+'" data-full-width="'+media.width+'" data-full-height="'+media.height+'">';
    html+=media.sections.map((part,i)=>'<a class="media-zoom-link" data-media-zoom data-full-width="'+media.width+'" data-image-y="'+part.y+'" href="'+esc(src)+'" aria-label="'+esc(label+' 본문 안내 '+(i+1)+'구간 원본 확대')+'"><img data-media-role="body" data-media-piece="'+i+'" src="'+esc(part.url)+'" alt="'+esc(label+' 본문 안내 '+(i+1)+'/'+media.sections.length+'구간')+'" width="'+part.width+'" height="'+part.height+'" loading="lazy" decoding="async" fetchpriority="low"></a>').join('');html+='</div>';edits.push({start:block.start,end:block.end,html});counts.segments+=media.sections.length;
   }else{
    let raw=s.slice(block.start,block.end);raw=raw.replace(s.slice(im.start,im.openEnd),attribute(s.slice(im.start,im.openEnd),'alt',label+(role==='map'?' 지도':' 본문 안내')));
    edits.push({start:block.start,end:block.end,html:'<a class="media-zoom-link" data-media-zoom data-full-width="'+esc(im.attrs.width)+'" data-image-y="0" href="'+esc(src)+'" aria-label="'+esc(label+(role==='map'?' 지도 원본 확대':' 본문 원본 확대'))+'">'+raw+'</a>'});
   }
   if(role==='map'){
    counts.maps++;const figure=ancestor(im,'figure');
    if(figure&&row){
     const visit=review.visits.find(v=>v.name===row['센터명']&&v.address===row['센터 주소']);
     const caption='<figcaption class="crawl-media-caption">'+esc(row['센터명'])+' · <span>'+esc(row['센터 주소'])+'</span><br>통합 상담 <a href="tel:010-6839-8283">010-6839-8283</a> · 방문할 지점과 학년을 말씀해 주세요.'+(visit?.directions?'<br>'+esc(visit.directions):'')+'<br>지도를 누르면 원본 크기로 읽을 수 있습니다. 방문 전 현재 주소와 이동 경로를 확인해 주세요.</figcaption>';
     edits.push({start:figure.closeStart,end:figure.closeStart,html:caption});
    }
   }
  }
  const teacher=nodes.find(n=>n.attrs.id==='center-teachers');
  if(teacher&&row){
   const link=nodes.find(n=>n.tag==='a'&&n.start>teacher.start&&n.end<teacher.end&&n.attrs.href?.startsWith('/선생님찾기/'));const slug=link?decodeURIComponent(link.attrs.href.split('/')[2]):null;const branch=review.branches[slug];
   if(branch&&branch.site_center===row['센터명']&&branch.address===row['센터 주소']){
    const para=nodes.filter(n=>n.tag==='p'&&n.start>teacher.start&&n.end<teacher.end).at(-1);
    if(para){const teachers=branch.teachers.slice(0,3);let html='<p>'+esc(branch.name)+' 소개에 실린 지도 키워드를 보고 학생에게 필요한 질문을 골라 보세요.</p><ul class="crawl-teacher-focus">'+teachers.map(t=>'<li>'+esc(t.name)+' 선생님: '+esc(t.keywords.join(' · '))+'</li>').join('')+'</ul><p>학생이 막힌 풀이와 최근 학습 기록을 함께 가져오면 어떤 설명·점검이 필요한지 질문하기 좋습니다. 희망 과목의 담당 교사와 현재 배정 여부는 상담에서 확인해 주세요.</p>';edits.push({start:para.start,end:para.end,html});counts.teacherFacts++}
   }
  }
  if(parts[0]==='전국학원'&&parts[1]==='와와학습코칭센터'&&row){const school=nodes.find(n=>n.attrs.id==='school-information');if(school){const html=schoolTable(row);if(html){edits.push({start:school.closeStart,end:school.closeStart,html});counts.schoolTables++}}}
 }
 const pngImages=nodes.filter(n=>n.tag==='img'&&ancestor(n,'main')&&review.png[imagePath(n.attrs.src||'',name)]?.variant);
 for(const im of pngImages){if(ancestor(im,'picture')||ancestor(im,'a'))throw Error('PNG has existing wrapper needing review');const src=imagePath(im.attrs.src,name),entry=review.png[src];const raw=s.slice(im.start,im.end);edits.push({start:im.start,end:im.end,html:'<a class="media-zoom-link" data-media-zoom data-full-width="'+entry.width+'" data-image-y="0" href="'+esc(src)+'" aria-label="'+esc(im.attrs.alt+' 원본 확대')+'"><picture><source type="image/webp" srcset="'+esc(entry.variant.url)+'">'+raw+'</picture></a>'});counts.png++}
 if(name==='전국학원/와와학습코칭센터/index.html'){
  const groups=nodes.filter(n=>n.tag==='h3'&&n.parent?.attrs.class==='find-group-heading');const links=[];
  groups.forEach((h,i)=>{const id='crawl-region-'+(i+1),label=plain(s.slice(h.openEnd,h.closeStart));links.push({id,label});edits.push({start:h.start,end:h.openEnd,html:attribute(s.slice(h.start,h.openEnd),'id',id)})});
  const section=nodes.find(n=>n.attrs.id==='center-directory');const heading=nodes.find(n=>n.tag==='div'&&n.parent===section&&n.attrs.class==='section-head');if(heading&&links.length){edits.push({start:heading.end,end:heading.end,html:'<nav class="crawl-region-links" aria-label="센터 주소 지역 바로가기">'+links.map(x=>'<a href="#'+x.id+'">'+esc(x.label)+' 동네 안내</a>').join('')+'</nav>'});counts.regions=links.length}
 }
 if(name==='index.html'){
  const hero=nodes.find(n=>n.tag==='section'&&n.parent===main);if(hero){const regions=[...new Set(Object.values(review.locals).map(r=>r['지역']))];const order=['서울','경기','인천','대전','충남','세종','충북','대구','울산','부산','경남','경북','전북','전남','광주','강원','제주'];
   // Match the directory's actual region headings, not an inferred geographic order.
   // Read the immutable input so concurrent public writes cannot truncate the directory snapshot.
   const directory=fs.readFileSync(path.join(root,'전국학원/와와학습코칭센터/index.html'),'utf8');const headings=parseHTML(directory).filter(n=>n.tag==='h3'&&n.parent?.attrs.class==='find-group-heading');const entries=headings.map((h,i)=>({label:plain(directory.slice(h.openEnd,h.closeStart)),id:'crawl-region-'+(i+1)}));
   edits.push({start:hero.end,end:hero.end,html:'<nav class="section" aria-label="지역별 동네와 센터 찾기"><p><a class="btn btn-ghost" href="/전국학원/와와학습코칭센터/">지역별 동네·센터 안내 전체 보기</a></p><div class="crawl-region-links">'+entries.map(x=>'<a href="/전국학원/와와학습코칭센터/#'+x.id+'">'+esc(x.label)+' 동네·센터</a>').join('')+'</div></nav>'});counts.regions=entries.length}
 }
 const photo=registeredPhoto(s,name,review);if(!edits.length&&photo===s)return {html:s,changed:false};
 s=registeredPhoto(reserveSections(replaceSpans(s,edits)),name,review);s=s.replace('<main','<main data-crawl-enhanced="20261007"');
 s=s.replace(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g,(raw,json)=>{const data=JSON.parse(json);for(const n of data['@graph']||[]){if(['WebPage','Article','CollectionPage','ContactPage'].includes(n['@type'])&&n.dateModified)n.dateModified=review.date}return raw.replace(json,JSON.stringify(data))});
 s=s.replace('</head>','<link rel="stylesheet" href="'+review.css+'"><script defer src="'+review.js+'"></script></head>');
 return {html:s,changed:true,counts};
}
export async function enhanceDirectory(){
 const publicRoot=path.join(root,'.public-release'),review=JSON.parse(fs.readFileSync(path.join(root,'crawl-content-review.json'),'utf8'));const manifest=JSON.parse(fs.readFileSync(path.join(root,'release-public-manifest.json'),'utf8'));const changed=[],counts={};
 const names=Object.keys(manifest.files).filter(n=>n.endsWith('.html'));let cursor=0;await Promise.all(Array.from({length:12},async()=>{while(cursor<names.length){const name=names[cursor++],file=path.join(publicRoot,name),s=await fs.promises.readFile(file,'utf8'),result=enhanceHTML(s,name,review);if(result.changed){await fs.promises.writeFile(file,result.html);changed.push(routeOf(name));for(const [k,v] of Object.entries(result.counts))counts[k]=(counts[k]||0)+v}}}));
 const paths=new Set(changed);const file=path.join(publicRoot,'sitemap.xml');let sitemap=fs.readFileSync(file,'utf8');sitemap=sitemap.replace(/<url>[\s\S]*?<\/url>/g,entry=>{const loc=entry.match(/<loc>([^<]+)<\/loc>/)?.[1];if(!loc||!paths.has(decodeURIComponent(new URL(loc).pathname)))return entry;return /<lastmod>/.test(entry)?entry.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+review.date+'</lastmod>'):entry.replace('</loc>','</loc><lastmod>'+review.date+'</lastmod>')});fs.writeFileSync(file,sitemap);return {changedPages:changed.length,counts,changedRoutes:changed};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){const report=await enhanceDirectory();console.log(JSON.stringify({changedPages:report.changedPages,counts:report.counts}));}
