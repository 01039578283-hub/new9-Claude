/** Notify only reviewed changes, after production verification. An HTTP receipt is not indexing. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url));
const arg=name=>process.argv.find(x=>x.startsWith('--'+name+'='))?.split('=').slice(1).join('=');
const commit=arg('commit'),receipt=arg('receipt'),dry=process.argv.includes('--dry-run');
if(!receipt||!path.isAbsolute(receipt))throw Error('Provide an absolute --receipt path outside the public output.');
if(fs.existsSync(receipt)){console.log('Receipt already exists; no repeat notification was sent.');process.exit(0);}
const review=JSON.parse(fs.readFileSync(path.join(root,'seo-geo-review.json'),'utf8'));
const base='https://'+review.host;
const xml=fs.readFileSync(path.join(root,'.public-release','sitemap.xml'),'utf8');
const urls=[...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1]).filter(u=>Object.hasOwn(review.pages,decodeURIComponent(new URL(u).pathname).slice(1)+'index.html'));
if(urls.length!==Object.keys(review.pages).length||urls.length>10000)throw Error('Notification list differs from reviewed changed pages.');
const payload={host:review.host,key:review.indexNowKey,keyLocation:base+'/'+review.indexNowKey+'.txt',urlList:urls};
const hash=createHash('sha256').update(JSON.stringify(payload)).digest('hex');
if(dry){console.log(JSON.stringify({dryRun:true,urls:urls.length,payloadSHA256:hash,doesNotGuaranteeIndexing:true}));process.exit(0);}
if(!/^[a-f0-9]{40}$/.test(commit||''))throw Error('Pass the verified production commit with --commit.');
const head=spawnSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'});
if(head.status!==0||head.stdout.trim()!==commit)throw Error('Working commit differs from verified deployment.');
const key=await fetch(payload.keyLocation,{signal:AbortSignal.timeout(30000)});
if(key.status!==200||(await key.text()).trim()!==review.indexNowKey)throw Error('Public ownership file is not ready.');
const check=await fetch(base+'/',{signal:AbortSignal.timeout(30000)});
if(check.status!==200||!(await check.text()).includes('data-answer-review="20261020"'))throw Error('Published answer content is not ready.');
const log={commit,at:new Date().toISOString(),urls:urls.length,payloadSHA256:hash,state:'sending',indexingConfirmed:false};
fs.writeFileSync(receipt,JSON.stringify(log,null,2));
try{
 const r=await fetch('https://searchadvisor.naver.com/indexnow',{method:'POST',headers:{'Content-Type':'application/json; charset=utf-8'},body:JSON.stringify(payload),signal:AbortSignal.timeout(60000)});
 log.status=r.status;log.response=(await r.text()).slice(0,2000);log.state=r.status===200?'notification_received':r.status===202?'key_verification_pending':'notification_error';
 fs.writeFileSync(receipt,JSON.stringify(log,null,2));console.log(JSON.stringify(log));if(![200,202].includes(r.status))process.exitCode=1;
}catch(e){log.state='delivery_unknown';log.error=String(e);fs.writeFileSync(receipt,JSON.stringify(log,null,2));throw e;}
