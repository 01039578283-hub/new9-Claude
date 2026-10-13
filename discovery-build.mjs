/** Reviewed, bounded content and navigation improvements. Original HTML and all images are retained as inputs. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {parseHTML} from './image-order-build.mjs';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,'.public-release');
const review=JSON.parse(fs.readFileSync(path.join(root,'discovery-review.json'),'utf8'));
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const text=s=>s.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
const within=(n,p)=>n.start>p.start&&n.end<=p.end;
const route=name=>name==='index.html'?'/':'/'+name.replace(/index\.html$/,'');
const link=p=>p.split('/').map(encodeURIComponent).join('/');
function edits(s,changes){changes.sort((a,b)=>b.start-a.start||b.end-a.end);let last=s.length+1;for(const c of changes){if(c.end>last)throw Error('Overlapping discovery edits');s=s.slice(0,c.start)+c.html+s.slice(c.end);last=c.start}return s;}
function worksheet(profile,grade,subject,row,oldHeading){
 const card=(title,evidence,question)=>'<article class="study-review-card"><h3>'+esc(title)+'</h3><dl><dt>학생이 가져올 기록</dt><dd>'+esc(evidence)+'</dd><dt>상담에서 물어볼 질문</dt><dd>'+esc(question)+'</dd></dl></article>';
 const listed=row.grades[subject]?.includes(grade),status=listed?'자료상 '+subject+' 가능 학년에 '+grade+' 항목이 있습니다. 현재 반 편성·담당 교사·수업 시간은 상담에서 확인해 주세요.':'자료에서 '+grade+' '+subject+' 수강 여부를 확정할 수 없습니다. 학습 상담 전에 현재 수강 가능한지 먼저 문의해 주세요.';
 return '<section class="section" id="consultation-example" data-study-worksheet="20261013"><div class="section-head"><h2>'+esc(oldHeading)+'</h2><p class="lead">'+grade+' '+subject+' 상담에서는 최근에 배운 자료 한 가지를 골라 학생의 풀이·읽기 흔적을 보여 주세요. 아래는 상담 질문을 준비하는 예시이며, 지점의 실제 수업 구성이나 학생 사례를 뜻하지 않습니다.</p></div><div class="study-review-grid">'+card(profile.record,profile.evidence,profile.question)+card(profile.second,profile.secondEvidence,profile.secondQuestion)+'</div><p class="study-review-note">'+esc(row['센터명'])+' 안내: '+esc(status)+'</p><p>보호자는 학교·통학 일정과 공부할 수 있는 시간을 함께 적어 오세요. 상담 후에는 먼저 보완할 내용 한 가지, 학생이 혼자 다시 해볼 과제, 다음 확인 시점을 기록하면 제안받은 계획을 비교하기 좋습니다.</p><div class="study-review-links"><a class="btn btn-ghost" href="/학습가이드/'+profile.guide+'/">'+esc(review.guideTitles[profile.guide])+'</a><a class="btn btn-ghost" href="/학습가이드/first-consultation/">첫 상담에서 확인할 질문과 준비 자료</a></div></section>';
}
function branchFacts(branch){
 const r=branch.row,neighborhood=branch.local;
 const subjects=Object.entries(r.grades).map(([subject,grades])=>{
  const paths=['수학','영어'].includes(subject)?grades.filter(g=>review.availablePages.includes('과목별학원/'+g+subject+'학원/'+neighborhood+'/index.html')).map(g=>'<a href="'+link('/과목별학원/'+g+subject+'학원/'+neighborhood+'/')+'">'+esc(neighborhood+' '+g+' '+subject+' 안내')+'</a>').join(''):'';
  return '<div class="study-branch-subject"><h3>'+esc(subject)+' 가능 학년</h3><p>'+esc(grades.length?grades.join(', '):'자료에 가능 학년이 기재되어 있지 않습니다. 현재 운영 여부는 지점에 확인해 주세요.')+'</p>'+(paths?'<div class="study-grade-links">'+paths+'</div>':'')+'</div>';
 }).join('');
 return '<div class="study-branch-facts" data-study-branch="20261013"><dl><dt>안내 센터</dt><dd>'+esc(r['센터명'])+'</dd><dt>방문 주소</dt><dd>'+esc(r['센터 주소'])+'</dd><dt>등록 학원명</dt><dd>'+esc(r['교육지원청명칭'])+'</dd><dt>등록번호</dt><dd>'+esc(r['교육지원청 등록번호'])+'</dd></dl><p>아래는 제공된 센터 자료의 과목별 가능 학년입니다. 현재 모집·시간표·담당 교사의 확정 안내가 아니므로 수강 조건은 지점 상담에서 확인해 주세요.</p>'+subjects+(branch.directions?'<p>찾아오는 길: '+esc(branch.directions)+' 방문 전 현재 주소와 건물 안내를 함께 확인해 주세요.</p>':'')+'<p><a href="'+esc(r['센터 교습비'])+'" target="_blank" rel="noopener noreferrer">'+esc(branch.name)+' 교습비 자료 확인</a> · 과목·수업 시간·횟수와 교재비 등 별도 비용을 함께 확인하세요.</p></div>';
}
export function improve(source,name){
 if(source.includes('data-discovery-review="20261013"'))return {html:source,changed:false};
 let s=source;const ns=parseHTML(s),changes=[],counts={};const main=ns.find(n=>n.tag==='main');if(!main)return {html:s,changed:false};
 const parts=name.split('/'),profile=parts[0]==='과목별학원'&&parts.length===4?review.profiles[parts[1].replace(/학원$/,'')]:null;
 const example=ns.find(n=>n.attrs.id==='consultation-example');
 if(profile&&example){
  if(ns.some(n=>n.tag==='img'&&within(n,example)))throw Error('Cannot replace a worksheet containing images '+name);
  const match=parts[1].match(/^([초중고]\d)(수학|영어)학원$/),h=ns.find(n=>n.tag==='h2'&&within(n,example));
  if(!match||!h||!review.locals[parts[2]])throw Error('Unreviewed learning profile '+name);
  changes.push({start:example.start,end:example.end,html:worksheet(profile,match[1],match[2],review.locals[parts[2]],text(s.slice(h.openEnd,h.closeStart)))});counts.worksheets=1;
 }
 const branch=review.branches[name],info=ns.find(n=>n.attrs.id==='branch-information');
 if(branch){if(!info)throw Error('Missing branch section '+name);changes.push({start:info.closeStart,end:info.closeStart,html:branchFacts(branch)});counts.branchFacts=1;}
 if(name.startsWith('학습커리큘럼/')){
  const hero=ns.find(n=>n.parent===main&&n.tag==='header'),following=hero?ns.find(n=>n.parent===main&&n.tag==='p'&&n.start>=hero.end):null;
  const leads=hero?ns.filter(n=>n.tag==='p'&&within(n,hero)):[];
  if(following&&leads.some(n=>text(s.slice(n.openEnd,n.closeStart))===text(s.slice(following.openEnd,following.closeStart)))){changes.push({start:following.start,end:following.end,html:''});counts.duplicateLead=1;}
 }
 if(parts[0]==='전국학원'&&parts[1]==='와와학습코칭센터'&&parts.length===4){
  const info=ns.find(n=>n.attrs.id==='center-information');
  for(const article of ns.filter(n=>n.tag==='article'&&info&&within(n,info))){
   const tag=ns.find(n=>n.tag==='span'&&n.attrs.class==='tag'&&within(n,article)),h=ns.find(n=>n.tag==='h3'&&within(n,article));if(!tag||!h)continue;
   const label=text(s.slice(tag.openEnd,tag.closeStart));if(!label.endsWith('가능 학년'))continue;
   changes.push({start:tag.start,end:tag.end,html:'<h3>'+esc(label)+'</h3>'},{start:h.start,end:h.end,html:'<p>'+s.slice(h.openEnd,h.closeStart)+'</p>'});counts.subjectHeadings=(counts.subjectHeadings||0)+1;
  }
 }
 s=edits(s,changes);
 // Only existing, non-content navigation parameters are removed from links. Legacy URLs remain valid.
 let context=false;
 s=s.replace(/<a\b[^>]*>/g,tag=>{
  const n=parseHTML(tag)[0],href=n?.attrs.href;if(!href||!href.includes('?'))return tag;
  const url=new URL(href,'https://'+review.host+route(name));if(url.hostname!==review.host||!review.contextRoutes.includes(decodeURIComponent(url.pathname)))return tag;
  const keys=[...url.searchParams.keys()];if(!keys.length||keys.some(k=>!review.contextKeys.includes(k)))throw Error('Unreviewed navigation query '+href);
  const canonical=url.pathname+url.hash;counts.contextLinks=(counts.contextLinks||0)+1;context=true;
  return tag.replace(/\bhref\s*=\s*(?:"[^"]*"|'[^']*')/,'href="'+esc(canonical)+'" data-study-context="'+esc(url.searchParams.toString())+'"');
 });
 s=s.replace(/<script\b[^>]*\bsrc="[^"]*"[^>]*>/g,tag=>{const src=parseHTML(tag)[0].attrs.src,u=new URL(src,'https://'+review.host+route(name)),asset=review.scripts[u.pathname];if(!asset||u.hostname!==review.host)return tag;context=true;counts.contextReceiver=1;return tag.replace(/\bsrc="[^"]*"/,'src="'+asset+'"');});
 for(const [wrong,right] of Object.entries(review.corrections)){if(s.includes(wrong)){s=s.replaceAll(wrong,right);counts.copyCorrections=(counts.copyCorrections||0)+1;}}
 if(s===source)return {html:s,changed:false,counts};
 if(context)s=s.replace('</head>','<script defer src="'+review.contextScript+'"></script></head>');
 // Context receivers are deferred and earlier in the head; initialize context before them.
 if(context){s=s.replace('<script defer src="'+review.contextScript+'"></script>','');s=s.replace(/<head\b[^>]*>/,tag=>tag+'<script defer src="'+review.contextScript+'"></script>');}
 if(counts.worksheets||counts.branchFacts)s=s.replace('</head>','<link rel="stylesheet" href="'+review.css+'"></head>');
 s=s.replace('<main','<main data-discovery-review="20261013"');
 s=s.replace(/(<script\b[^>]*type="application\/ld\+json"[^>]*>)([\s\S]*?)(<\/script>)/g,(raw,open,json,close)=>{
  const data=JSON.parse(json);let modified=false;const graph=data['@graph']||[data];
  for(const x of graph)if(['WebPage','Article','CollectionPage','ContactPage'].includes(x['@type'])&&x.dateModified){x.dateModified=review.date;modified=true;}
  return modified?open+JSON.stringify(data)+close:raw;
 });
 return {html:s,changed:true,counts};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(!process.argv.includes('--apply-only')){const r=spawnSync(process.execPath,['thumbnail-build.mjs'],{cwd:root,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status??1);}
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'release-public-manifest.json'),'utf8'));const files=Object.keys(manifest.files).filter(n=>n.endsWith('.html'));let cursor=0;const changed=[],counts={};
 await Promise.all(Array.from({length:12},async()=>{while(cursor<files.length){const name=files[cursor++],file=path.join(out,name),s=await fs.promises.readFile(file,'utf8'),r=improve(s,name);if(r.changed){await fs.promises.writeFile(file,r.html);changed.push(route(name));for(const [k,v] of Object.entries(r.counts))counts[k]=(counts[k]||0)+v;}}}));
 const paths=new Set(changed),sitemap=path.join(out,'sitemap.xml');let xml=fs.readFileSync(sitemap,'utf8');xml=xml.replace(/<url>[\s\S]*?<\/url>/g,entry=>{const loc=entry.match(/<loc>([^<]+)<\/loc>/)?.[1];if(!loc||!paths.has(decodeURIComponent(new URL(loc).pathname)))return entry;return entry.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+review.date+'</lastmod>');});fs.writeFileSync(sitemap,xml);
 console.log(JSON.stringify({discoveryPages:changed.length,counts,canonicalURLsUnchanged:true,imageFilesUnchanged:true}));
}
