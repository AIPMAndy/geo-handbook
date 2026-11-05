/** GEO Handbook V2 offline-only browser tools. No API requests or telemetry. */
(function(){
'use strict';
const $=(x)=>document.querySelector(x);
const esc=(v)=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const preview=$('#htmlInput'),auditResult=$('#htmlAuditResults');
const badDemo='<html><head><meta name="robots" content="noindex,nofollow"><title></title></head><body><div>仅教学演示，故意缺少 H1、canonical 与描述。</div></body></html>';
$('#loadBrokenHtml')?.addEventListener('click',()=>{preview.value=badDemo;$('#htmlSiteUrl').value='https://example.com/article';preview.focus()});
function runHtmlAudit(){
  if(!auditResult||!preview)return;
  const input=preview.value;
  if(!input.trim()){auditResult.innerHTML='<h2>请先粘贴 HTML 源代码</h2><p>在浏览器查看源代码（View page source），复制 HTML。此工具不会联网。</p>';return;}
  if(input.length>2097152){auditResult.innerHTML='<h2>文件过大</h2><p>本地诊断限定为 2 MiB 的 HTML。</p>';return;}
  const doc=new DOMParser().parseFromString(input,'text/html');
  const title=doc.title.trim();
  const desc=doc.querySelector('meta[name="description" i]')?.content?.trim()||'';
  const robots=(doc.querySelector('meta[name="robots" i]')?.content||'').toLowerCase();
  const canonical=doc.querySelector('link[rel="canonical" i]')?.href||'';
  const main=doc.querySelector('main')||doc.body;
  const bodyText=(main?.textContent||'').replace(/\s+/g,' ').trim();
  const h1=[...doc.querySelectorAll('h1')];const issues=[];
  function add(level,what,action){issues.push({level,what,action})}
  if(!title)add('高','页面缺少非空 title','写准确、唯一的页面标题');
  if(h1.length!==1)add('中',`发现 ${h1.length} 个 H1`,'让页面有清晰主标题，优先考虑可读性');
  if(!desc)add('低','没有 meta description','描述用户能获得的独特价值');
  if(!canonical)add('中','没有 canonical','针对重要的规范页评估添加 canonical');
  const inputUrl=$('#htmlSiteUrl')?.value||'';
  if(canonical&&inputUrl&&canonical.replace(/\/$/,'')!==inputUrl.replace(/\/$/,''))add('中','canonical 与输入网页 URL 不同','确认是否有意指向另一规范页');
  if(/(?:^|[\s,])noindex(?:[\s,]|$)/.test(robots))add('严重','存在 noindex','确认公开页面是否误设；不要修改需要隐藏的页面');
  if(bodyText.length<150)add('中',`HTML 正文约 ${bodyText.length} 字符`,'检查是否只在 JavaScript 中呈现核心正文');
  if([...doc.images].some(i=>!i.hasAttribute('alt')))add('低','部分图片没有 alt 属性','说明内容图片，装饰图按用途处理');
  let schemaCount=0,invalidSchema=0;
  [...doc.querySelectorAll('script[type="application/ld+json" i]')].forEach(s=>{
    schemaCount++;
    try{JSON.parse(s.textContent)}catch{invalidSchema++;add('中','JSON-LD 无法被 JSON 解析','修正 JSON 语法，并与页面真实事实核对')}
  });
  const summary=`<div class="statbar"><div class="stat"><strong>${issues.length}</strong><span>需检查的提示</span></div><div class="stat"><strong>${h1.length}</strong><span>H1</span></div><div class="stat"><strong>${bodyText.length}</strong><span>正文字符</span></div><div class="stat"><strong>${schemaCount-invalidSchema}/${schemaCount}</strong><span>有效 JSON-LD</span></div></div>`;
  const rows=issues.length?issues.map(i=>`<div class="notice"><strong>[${esc(i.level)}] ${esc(i.what)}</strong><p>${esc(i.action)}</p></div>`).join(''):'<div class="notice"><strong>未检测到上述结构问题</strong><p>这只意味着静态 HTML 初筛未报警，不代表 Google 已索引或 AI 已引用。</p></div>';
  auditResult.innerHTML=`<h2>本地 HTML 结构检查</h2>${summary}<p><strong>标题：</strong>${esc(title||'无')}<br><strong>描述：</strong>${esc(desc||'无')}<br><strong>canonical：</strong>${esc(canonical||'无')}</p><h3>逐条修复建议</h3>${rows}<p class="tiny">注意：不检测 HTTP 状态、robots.txt、CDN、真实爬虫、搜索索引、AI 引用或排名。</p>`;
}
$('#runHtmlAudit')?.addEventListener('click',runHtmlAudit);

const required=['date','platform','region','phase','question_type','ai_answer_triggered','query','brand_mentioned','owned_url_cited','citation_url','evidence'];
function parseCsv(raw){
  // RFC4180-ish CSV state machine; correctly handles quoted commas, embedded newlines, doubled quotes.
  const text=raw.replace(/^\ufeff/,'');const rows=[];let row=[],field='',quote=false;
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(quote){if(c==='"'&&text[i+1]==='"'){field+='"';i++}else if(c==='"'){quote=false}else field+=c}
    else if(c==='"'&&field===''){quote=true}
    else if(c===','){row.push(field);field=''}
    else if(c==='\r'&&text[i+1]==='\n'){row.push(field);rows.push(row);row=[];field='';i++}
    else if(c==='\n'||c==='\r'){row.push(field);rows.push(row);row=[];field=''}
    else field+=c;
  }
  if(quote)throw Error('CSV 有未闭合的双引号');
  if(field!==''||row.length){row.push(field);rows.push(row)}
  if(!rows.length)throw Error('CSV 没有数据');
  const cols=rows.shift();const missing=required.filter(k=>!cols.includes(k));
  if(missing.length)throw Error('CSV 缺少必要列：'+missing.join(', '));
  return rows.filter(r=>r.some(x=>x.trim())).map(r=>Object.fromEntries(cols.map((c,i)=>[c,(r[i]||'').trim()])));
}
function yes(s){return ['1','yes','true','是'].includes(String(s||'').toLowerCase())}
function csvSummary(rows,isDemo){
  const target=$('#csvResults');if(!target)return;
  if(rows.length>20000)throw Error('一次最多导入 20,000 行；请按季度切分文件');
  const excluded={brand:0,notTriggered:0};const valid=[];let incomplete=0;
  for(const r of rows){
    if(r.question_type!=='natural'){excluded.brand++;continue}
    if(!yes(r.ai_answer_triggered)){excluded.notTriggered++;continue}
    if(yes(r.owned_url_cited)&&!r.citation_url)incomplete++;
    valid.push(r);
  }
  const groups=new Map();
  valid.forEach(r=>{const key=JSON.stringify([r.phase,r.platform,r.region]);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(r)});
  const sorted=[...groups.entries()].sort((a,b)=>a[0].localeCompare(b[0]));
  const table=sorted.map(([key,g])=>{
    const [phase,platform,region]=JSON.parse(key);
    const mentions=g.filter(r=>yes(r.brand_mentioned)).length;
    const citations=g.filter(r=>yes(r.owned_url_cited)&&r.citation_url.trim()).length;
    return `<tr><td>${esc(phase)}</td><td>${esc(platform)}</td><td>${esc(region)}</td><td>${g.length}</td><td>${mentions} / ${(100*mentions/g.length).toFixed(1)}%</td><td>${citations} / ${(100*citations/g.length).toFixed(1)}%</td></tr>`;
  }).join('');
  // Check whether exact questions exist in both baseline and after for the same platform/region.
  const questionSets=new Map();
  valid.forEach(r=>{const key=JSON.stringify([r.platform,r.region,r.query]);if(!questionSets.has(key))questionSets.set(key,new Set());questionSets.get(key).add(r.phase)});
  const paired=[...questionSets.values()].filter(x=>x.has('baseline')&&x.has('after')).length;
  target.innerHTML=`<h2>${isDemo?'合成样例分析（绝非实际业绩）':'本地 CSV 分析结果'}</h2>
  <div class="statbar"><div class="stat"><strong>${rows.length}</strong><span>文件行数</span></div><div class="stat"><strong>${valid.length}</strong><span>有效自然提问</span></div><div class="stat"><strong>${excluded.brand}</strong><span>排除品牌直搜</span></div><div class="stat"><strong>${excluded.notTriggered}</strong><span>排除未触发</span></div></div>
  <p class="tiny">引用=同时标记「是」且填写真实自有 URL；有 ${incomplete} 条引用标记缺少 URL，需人工补证。</p>
  <div class="tablewrap"><table><thead><tr><th>阶段</th><th>平台</th><th>地区</th><th>有效样本</th><th>品牌提及</th><th>自有 URL 引用</th></tr></thead><tbody>${table||'<tr><td colspan="6">没有可统计的有效自然回答</td></tr>'}</tbody></table></div>
  <div class="notice">找到 ${paired} 个相同平台、地区及问题原文的前后配对问法。若为 0，则不能把两组百分比当作同题复测。就算存在配对，也无法仅凭本表证明因果关系。</div>
  <p class="tiny">本地分析不核验 URL 属于谁，也不使用 AI 平台内部排名数据。请保留截图证据并人工验证。</p>`;
}
const demoRows=[];
for(let i=0;i<12;i++)demoRows.push({date:i<6?'2026-10-01':'2026-11-01',platform:i%2?'ChatGPT Search':'Bing/Copilot',region:'zh-CN/中国大陆',phase:i<6?'baseline':'after',question_type:i===3?'brand':'natural',ai_answer_triggered:i===10?'0':'1',query:`教学问法 ${i%6}`,brand_mentioned:i%4===0?'1':'0',owned_url_cited:i%5===0?'1':'0',citation_url:i%5===0?'https://example.com/article':'',evidence:'SYNTHETIC'});
$('#loadDemoCsv')?.addEventListener('click',()=>csvSummary(demoRows,true));
$('#reportCsv')?.addEventListener('change',async(e)=>{
  const file=e.target.files?.[0];if(!file)return;
  const result=$('#csvResults');
  try{
    if(file.size>2097152)throw Error('CSV 文件超过 2 MiB；请按周期拆分');
    const rows=parseCsv(await file.text());csvSummary(rows,false);
  }catch(err){if(result)result.innerHTML='<h2>CSV 文件无法分析</h2><p>'+esc(err.message||err)+'</p><p class="tiny">请使用本项目监测工具导出的原始 CSV，核对是否包含 11 个必填列。</p>'}
});
})();
// Quote calculator module. Intentionally separate from the manual AI metrics.
(function(){'use strict';
const btn=document.getElementById('calculateQuote');if(!btn)return;
function recalc(){
  const ids=['quoteHours','quoteHourly','quoteOther','quoteQa','quoteMargin'];
  const v=ids.map(k=>Number(document.getElementById(k).value));
  const box=document.getElementById('quoteResult');
  if(v.some(x=>!Number.isFinite(x)||x<0)||v[4]>90){box.textContent='请输入非负数；毛利率范围必须在 0–90%。';return}
  const [hours,rate,other,qa,margin]=v;
  if(hours>100000||rate>1000000||other>1e10||qa>1e10){box.textContent='数值异常：请核对单位和实际成本。';return}
  const direct=hours*rate, cost=direct+other+qa;
  if(!cost){box.textContent='所有成本都是 0，无法给出有意义的项目报价。请按真实情况填写。';return}
  const price=cost/(1-margin/100),profit=price-cost;
  const money=n=>new Intl.NumberFormat('zh-CN',{style:'currency',currency:'CNY',maximumFractionDigits:0}).format(n);
  box.innerHTML=`<h2>你的项目成本估算</h2><div class="statbar"><div class="stat"><strong>${money(cost)}</strong><span>估算完全成本</span></div><div class="stat"><strong>${money(price)}</strong><span>目标含毛利报价</span></div><div class="stat"><strong>${money(profit)}</strong><span>目标毛利额</span></div></div><p>公式：项目总成本 = 实际工时 × 小时内部成本 + 额外支出 + 质检预留；报价 = 成本 ÷ (1 − 目标毛利率)。</p><p class="tiny">此值只根据你的输入计算，未考虑税费、融资成本、应收账款回收或市场成交概率。不是官方/行业报价，更不保证客户接受。</p>`;
}
btn.addEventListener('click',recalc);
})();
