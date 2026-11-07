#!/usr/bin/env python3
"""Generate an original, operational GEO playbook as an additive Pages build step.

No external runtime dependencies or network access. Does not modify earlier
course content, page source generator, or count-constrained template catalogue.
"""
from __future__ import annotations
import html, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
SRC = ROOT / 'operations'
SITE = 'https://aipmandy.github.io/geo-handbook/'

MODULES = [
    ('01','建立可核验的品牌事实','先清楚，再传播',
     '把名称、服务边界、价格、交付地区、可引用案例和最新版本逐条登记。任何未经确认的事实不进入公开内容。',
     ['选一个在售产品或服务，列出 12 条会影响客户决策的陈述。',
      '给每条陈述指派审核人、有效期与公开证据，状态只允许 confirmed / pending / retired。',
      '对官网、介绍页、媒体资料和常见问答逐项核对，不一致的条目进入纠错队列。'],
     'brand-facts.csv','交付品牌事实表；每个公开事实都有审核人、有效日期和可查依据。'),
    ('02','找到最值得解决的客户问题','选择，不是铺量',
     '把用户真实提问与商业价值、证据完备度、当前表现缺口以及实现工时一起排序，避免批量覆盖同义问题。',
     ['从销售记录、客户访谈或站内搜索导出实际问题，注明来源。',
      '将同义问法归并成主问题；按客户需求、业务相关性、证据准备度、表现缺口和工作量评分。',
      '先实施排名最高的三个问题，剩余进入观察池，不以页数作为产出目标。'],
     'question-priority.csv','交付去重问题清单及优先级，前三个问题可在七天内发布或修复。'),
    ('03','建立跨平台的证据记录','先分母，后指标',
     '相同问题在不同平台、时间和地区的回答可能变化。保留原始答案、截图、链接、语言和触发状态，再评价结果。',
     ['为同一购买阶段建立固定测试题，每题设标准版本和对照版本。',
      '分平台记录采样时间、地区、账号状态、模型、是否联网、回答文本、提及、引用链接、竞品。',
      '先剔除品牌直搜、重复样本及未触发回答，再按平台独立计算指标。'],
     'answer-samples.csv','交付含可回溯原始证据的样本账本；指标均可按分母复算。'),
    ('04','把错误答案变成内容修复单','从现象追到信息缺口',
     '不要只截图抱怨模型。先核对内部事实，再追踪展示的出处及相互矛盾的页面，最后修复自己的事实材料。',
     ['记录错误陈述、准确答案、验证凭据和影响客户决策的程度。',
      '检查被引用的 URL 是否过期、遗漏范围或来源不可靠，识别可由企业控制的修复点。',
      '更新权威页面与问答，写入变更日志，按固定条件复测；无变化也保留失败记录。'],
     'correction-queue.csv','交付从错误观察到修复、复测的闭环工单，不承诺单次修正一定改变模型答案。'),
    ('05','按渠道配置内容与预算','根据边际收益调整',
     '官网是事实锚点，外部渠道仅在具有真实受众和可信内容时投入。把发布完成与被引用、访问、咨询区分开。',
     ['确定每种渠道对应的客户使用场景和内容资产，保持事实一致。',
      '将预算分为维护、验证和扩展；为每项投入定义停止条件与下一次复核日。',
      '记录发布时间、访问和咨询证据；若内容始终无引用或无有效客户行为，定位失败环节。'],
     'channel-decisions.csv','交付渠道与预算决策表，能解释为什么继续、缩减或停止一项投入。'),
    ('06','明确人工与自动化边界','效率和责任同时设计',
     '自动化可以做资料清洗、草稿和差异比较；事实核验、预算、法律敏感内容与发布权限由指定负责人审批。',
     ['为每个节点标注人工执行、AI 辅助、自动执行和批准责任人。',
      '对自动输出建立输入证据检查、重复检查、事实核验和回滚机制。',
      '记录耗时、错误率、人工复核负担，只有净收益为正才扩展自动化。'],
     'review-ownership.csv','交付具备权限和回滚的执行责任表，自动化动作均可追责。'),
    ('07','用完整指标解释经营变化','观测、比较、谨慎归因',
     '一组指标覆盖可见性、事实准确性、引用有效性、站内行为、竞争对比和商业结果，保留因果边界。',
     ['确认指标定义、分母、数据源、时间窗及更新频率；不要把提及率当成交率。',
      '对照发布前后同条件问题集，至少记录技术改动、品牌活动与同期搜索波动。',
      '单独统计直接追踪线索、用户自报来源、未归因线索，不能将相关变化直接算成 GEO 带来的收入。'],
     'measurement-dictionary.csv','交付可复算的 KPI 字典和异常说明；报告可区分观察与因果主张。'),
    ('08','向客户移交可持续经营的资产','一次交付，长期可维护',
     '企业最终需要的不是一次漂亮报告，而是自有的事实库、内容、验证记录、权限说明和下一轮经营节奏。',
     ['确认交付包括已验证事实、修改页面、编辑稿、原始日志、看板、人员权限及操作手册。',
      '逐项确认归属、格式、访问方式、备份、敏感信息处理和后续维护负责人。',
      '建立 30/60/90 天回顾点，用新证据修订策略，并记录停止或扩展的理由。'],
     'handover-checklist.csv','交付完整资产清单和接手手册，客户不依赖单一执行人员即可维护。'),
]

H=lambda s:html.escape(str(s), quote=True)

def nav_insert(page: str, root='') -> str:
    """Add one primary link. Existing navigations are otherwise untouched."""
    target=f'{root}operations.html'
    if f'href="{target}"' not in page and f"href='{target}'" not in page:
        # Insert just before the existing templates link, if present.
        page=re.sub(r'(<a href=[\'\"]'+re.escape(root)+r'templates\.html[\'\"][^>]*>)',
                    f'<a href="{target}">企业实操</a>\\1',page,count=1)
    return page

def add_to_home(page: str) -> str:
    card='''<section class="section" id="operating-playbook"><div class="container"><div class="eyebrow">GEO OPERATIONS / EIGHT EXECUTABLE MODULES</div><h2>把 GEO 从教程，做到企业可以验收。</h2><p class="intro">事实核对、问题决策、平台采样、纠错闭环、预算调整、人工审批、指标归因、交付移交。每一步都有可下载的表格和检查条件。</p><div class="actions"><a class="btn" href="operations.html">进入企业实操系统 →</a></div></div></section>'''
    if 'id="operating-playbook"' not in page:
        page=page.replace('</main>',card+'</main>',1)
    return page

def module_html(x):
    no,title,tag,desc,steps,file_name,proof=x
    lis=''.join(f'<li>{H(s)}</li>' for s in steps)
    return f'''<article class="ops-card" id="step-{no}"><div class="ops-tag">MODULE {no} · {H(tag)}</div><h2>{H(title)}</h2><p>{H(desc)}</p><ol>{lis}</ol><div class="ops-proof"><strong>完成凭证</strong><span>{H(proof)}</span></div><a class="ops-link" href="downloads/operations/{H(file_name)}" download>下载模板 · {H(file_name)} ↗</a></article>'''

# Purely original demo values: no facts about real clients.
DEMO=[('高管 AI 转型怎么选辅导服务？',5,5,5,4,2),('AI 产品经理简历怎么准备？',4,5,4,3,2),('什么是 AI 产品化？',4,2,3,2,1)]

def build():
    DOCS.mkdir(parents=True,exist_ok=True)
    dest=DOCS/'downloads'/'operations';dest.mkdir(parents=True,exist_ok=True)
    for source in sorted(SRC.glob('*.csv')):shutil.copyfile(source,dest/source.name)
    # Do not need or change global CSS: a separate stylesheet works with the existing white theme.
    (DOCS/'assets'/'operations.css').write_text('''
.ops-hero{padding:84px 0 55px;background:linear-gradient(180deg,#fff,#fbfbfd)}
.ops-hero h1{font-size:clamp(38px,6vw,68px);line-height:1.13;letter-spacing:-.055em;max-width:970px;margin:12px 0 24px}
.ops-hero p{max-width:800px;font-size:18px;color:#6e6e73}.ops-overview{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}.ops-overview span{font-size:13px;background:#f5f5f7;border:1px solid #e6e6eb;border-radius:999px;padding:7px 13px}
.ops-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;padding:26px 0 70px}
.ops-card{background:#fff;border:1px solid #e8e8ee;border-radius:28px;padding:28px;box-shadow:0 10px 34px rgba(0,0,0,.035)}.ops-card h2{font-size:25px;letter-spacing:-.035em;line-height:1.3;margin:12px 0}.ops-card p{font-size:15px;color:#66666d}.ops-tag{font-size:11px;letter-spacing:.12em;font-weight:700;color:#85858b}.ops-card ol{margin:22px 0;padding-left:19px}.ops-card li{font-size:14px;line-height:1.8;padding:5px 0}.ops-proof{display:flex;gap:10px;flex-direction:column;border-top:1px solid #eeeef1;padding:17px 0}.ops-proof strong{font-size:12px}.ops-proof span{font-size:13px;color:#6e6e73}.ops-link{display:inline-block;font-size:13px;font-weight:650;color:#1d1d1f;text-decoration:underline;text-underline-offset:4px}
.ops-score{margin:0 0 80px;background:#f5f5f7;border-radius:30px;padding:35px}.ops-score h2{font-size:31px;letter-spacing:-.04em;margin:0 0 12px}.ops-score p{color:#6e6e73}.ops-form{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:22px}.ops-form label{display:block;font-size:13px;font-weight:600}.ops-form input{display:block;width:100%;border:1px solid #d9d9df;border-radius:12px;padding:10px;background:#fff;margin-top:6px}.ops-result{background:white;border-radius:17px;padding:22px;margin-top:18px;border:1px solid #e4e4e9}.ops-result strong{font-size:30px;letter-spacing:-.04em}.ops-safe{font-size:13px;color:#55555c;border-top:1px solid #e6e6ea;margin-top:24px;padding-top:16px}
@media(max-width:830px){.ops-grid{grid-template-columns:1fr}.ops-form{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:580px){.ops-hero{padding:56px 0 36px}.ops-hero h1{font-size:39px}.ops-hero p{font-size:16px}.ops-form{grid-template-columns:1fr}.ops-score{padding:23px}.ops-card{padding:23px}}
''',encoding='utf-8')
    scores='''<section class="container"><div class="ops-score" id="priority-tool"><div class="eyebrow">FREE PRACTICAL TOOL</div><h2>一个问题值不值得先做？</h2><p>填入 0–5 分。需求真实性、业务价值、证据准备程度、当前缺口越大越值得验证；工作量越高，优先级越低。仅用于排序，不预测 AI 排名。</p><div class="ops-form">
<label>问题内容<input type="text" id="qtext" placeholder="例如：企业如何选 GEO 咨询？" maxlength="150"></label>
<label>真实需求 0–5<input type="number" id="demand" min="0" max="5" value="3"></label>
<label>业务价值 0–5<input type="number" id="relevance" min="0" max="5" value="4"></label>
<label>现成证据 0–5<input type="number" id="evidence" min="0" max="5" value="3"></label>
<label>当前短板 0–5<input type="number" id="gap" min="0" max="5" value="3"></label>
<label>执行成本 0–5<input type="number" id="effort" min="0" max="5" value="2"></label></div>
<div class="actions"><button class="btn" type="button" id="scoreBtn">计算优先级</button><button class="btn alt" type="button" id="copyResult">复制结果</button></div><div id="scoreResult" class="ops-result" role="status" aria-live="polite">输入分数后开始计算。数据不上传服务器。</div><div class="ops-safe">计算式：需求×3＋价值×3＋证据×2＋短板×2－成本。人工判断优先于数字；没有真实客户问题或可信证据时，不能直接发布。</div></div></section>'''
    cards=''.join(module_html(x) for x in MODULES)
    js='''<script>(function(){"use strict";var result=document.getElementById("scoreResult"),last="";function val(id){var n=Number(document.getElementById(id).value);if(!Number.isFinite(n)||n<0||n>5)throw Error("每项分数必须在 0–5 之间");return n}document.getElementById("scoreBtn").addEventListener("click",function(){try{var d=val("demand"),r=val("relevance"),e=val("evidence"),g=val("gap"),w=val("effort");var score=d*3+r*3+e*2+g*2-w;var label=score>=33?"优先做最小实验":score>=22?"进入第二批验证":"暂缓，先补证据或需求";last=(document.getElementById("qtext").value.trim()||"未命名问题")+" | 得分 "+score+"/50 | "+label+" | 需求="+d+",价值="+r+",证据="+e+",缺口="+g+",成本="+w;result.textContent=last;}catch(err){result.textContent=err.message}});document.getElementById("copyResult").addEventListener("click",function(){if(!last)return;var text=last;if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(function(){result.textContent=text+"（已复制）"},function(){result.textContent=text+"（浏览器限制复制，请手动选中）"})}else result.textContent=text+"（请选择文字复制）"});})();</script>'''
    body=f'''<div class="ops-hero"><div class="container"><div class="eyebrow">OPERATIONS PLAYBOOK · ORIGINAL FIELD SYSTEM</div><h1>从品牌事实到商业结果。<br>一条真正可以审计的 GEO 链路。</h1><p>8 个核心模块、8 套表格、1 个本地优先级计算器。围绕真实客户问题，构建事实、可访问页面、持续监测和可移交资产；不把发布次数当成果。</p><div class="ops-overview"><span>事实质量</span><span>问题决策</span><span>多平台采样</span><span>错误纠正</span><span>渠道预算</span><span>人工审批</span><span>可复算数据</span><span>企业移交</span></div><div class="actions"><a class="btn" href="#step-01">从第一个模块开始</a><a class="btn alt" href="#priority-tool">打开免费评分工具</a></div></div></div><div class="container ops-grid">{cards}</div>{scores}'''
    # Use the existing site's nav/footer and only replace main body.
    main=DOCS/'index.html'
    index=main.read_text(encoding='utf-8')
    head=index.split('<main id="content">',1)[0] if '<main id="content">' in index else index.split('<main id=\'content\'>',1)[0]
    footer=index.split('</main>',1)[1]
    pagehead=head.replace('<title>','<title>企业 GEO 实操 | ',1)
    pagehead=pagehead.replace('</head>','<link rel="stylesheet" href="assets/operations.css"></head>',1)
    # update canonical and OG URL from the home URL, preserving rest.
    pagehead=pagehead.replace('geo-handbook/index.html','geo-handbook/operations.html')
    pagehead=nav_insert(pagehead)
    # Home page embeds app scripts at footer; harmless on operations page.
    document=pagehead+'<main id="content">'+body+'</main>'+footer
    document=document.replace('</body>',js+'</body>')
    (DOCS/'operations.html').write_text(document,encoding='utf-8')
    # Add entry points to all generated pages; protect against duplicate insertion.
    for p in sorted(DOCS.rglob('*.html')):
        if 'downloads' in p.parts or p.name=='operations.html':continue
        rel=p.relative_to(DOCS)
        root='../' if len(rel.parts)>1 else ''
        source=p.read_text(encoding='utf-8')
        patched=nav_insert(source,root)
        if p.name=='index.html':patched=add_to_home(patched)
        if patched!=source:p.write_text(patched,encoding='utf-8')
    sitemap=DOCS/'sitemap.xml'
    xml=sitemap.read_text(encoding='utf-8')
    url=SITE+'operations.html'
    if url not in xml:
        xml=xml.replace('</urlset>',f'<url><loc>{url}</loc></url>\n</urlset>')
        sitemap.write_text(xml,encoding='utf-8')
    print('Generated GEO operations page, eight templates, dedicated CSS and integrated navigation.')

if __name__=='__main__':build()
