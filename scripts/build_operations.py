#!/usr/bin/env python3
"""Build a reproducible GEO experiment studio (independent from editorial summaries).

This implementation is authored from observable web, measurement and experiment
requirements. It never loads third-party prose, tracking pixels, paid APIs or accounts.
"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
SOURCE = ROOT / 'operations'
DOWNLOADS = DOCS / 'downloads' / 'operations'
BASE_URL = 'https://aipmandy.github.io/geo-handbook/'

# Each experiment has a measurable question, a reproducible procedure, a file, and an exit test.
EXPERIMENTS = [
    {
        'id': 'E01', 'time': '25 分钟', 'name': '写出一个可证伪的 GEO 假设',
        'intro': '不要从「我要做 GEO」开始。先确定一个具体用户问题、一个待改的页面和一个可观察的结果。',
        'steps': [
            '从真实客服、销售记录或搜索查询中选一个问题，保留匿名化的原话来源。',
            '写成假设：某个页面的明确改动，可能提高特定 AI 搜索条件下的有效引用。',
            '先固定问题版本、观察平台、地区、日期和对照页面，再启动改动。',
        ],
        'pass': '实验编号、问题、观察窗口和对照条件齐全；没有真实问题来源时不通过。',
        'asset': '01-experiment-plan.csv',
    },
    {
        'id': 'E02', 'time': '30 分钟', 'name': '给目标网页做一次技术体检',
        'intro': '把「网页打不开」与「没有被 AI 推荐」分开处理。先确认网页有没有阻止被发现的基础问题。',
        'steps': [
            '用浏览器打开真实 URL，记录 HTTP 状态、主要正文是否无需登录可读。',
            '检查 title、主要标题、canonical、meta robots；针对真实站点核验根目录 robots.txt。',
            '核对页面中每个重要事实是否有可信证据，并记录证据缺口。',
        ],
        'pass': '有时间戳和页面版本；有阻断问题则先修复，不进入结果归因。',
        'asset': '02-page-readiness.csv',
    },
    {
        'id': 'E03', 'time': '40 分钟', 'name': '建立改动前的回答样本',
        'intro': '单次截图不能代表稳定表现。要记录具体运行条件，才能知道后续变化是否有比较意义。',
        'steps': [
            '用固定的非品牌问题提问；保存完整回答和原始可访问链接，注明 AI 平台与日期。',
            '对同一问题重复采样，不同平台、地区和语言分别建组。',
            '标注是否触发搜索、是否直接提及品牌、是否出现可验证的目标页面 URL。',
        ],
        'pass': '每个有效样本可回到原始答案；未触发搜索与品牌直搜不混入自然问题分母。',
        'asset': '03-answer-captures.csv',
    },
    {
        'id': 'E04', 'time': '45 分钟', 'name': '只修改一个关键内容因素',
        'intro': '一次改十个地方，结果变化了也不知道是什么原因。用最小改动构建第一轮证据。',
        'steps': [
            '从页面缺口中选一个主要因素，例如答案不直接、来源不清楚或页面结构混乱。',
            '保存改动前的版本、提交编号和改动后 URL，标注发布时间。',
            '能做对照就保留同主题的未改页面；不能做就明确注明本轮只能观察相关性。',
        ],
        'pass': '有可回滚的版本记录，且每项修改能够追溯到实验假设。',
        'asset': '04-change-ledger.csv',
    },
    {
        'id': 'E05', 'time': '30 分钟', 'name': '复测并做出继续或停止决定',
        'intro': '改变了内容，不等于改变了回答。按原来的样本条件复测，再分清哪些结论有依据。',
        'steps': [
            '使用相同的问题版本、平台、地区和触发条件重新采样，保留未出现引用的结果。',
            '逐个平台计算有效样本中「提及」和「目标页面 URL 引用」的比例，写明分子分母。',
            '输出三种结论之一：继续验证、修改假设、停止投入；备注同时期可能的其他变化。',
        ],
        'pass': '复测条件与基线可比较；任何效果结论必须链接到真实记录。',
        'asset': '05-review-decision.csv',
    },
    {
        'id': 'E06', 'time': '25 分钟', 'name': '把引用实验连接到真实客户行为',
        'intro': '只有引用率还不够。需要独立记录访问、咨询和签约，避免把所有新增收入算给 GEO。',
        'steps': [
            '为目标页面设置正常的咨询入口并按渠道归档访问事件，不采集不必要的个人隐私。',
            '区分用户自报「在 AI 里看到」、可追踪来源、无法判定来源三类证据。',
            '输出一页项目复盘：实验做了什么、真实观察到什么、无法证明什么、下一步是什么。',
        ],
        'pass': '每条商业事件有独立依据；不得把无来源的咨询自动归因到本次改动。',
        'asset': '06-outcome-trace.csv',
    },
]


def h(s: str) -> str:
    return html.escape(str(s), quote=True)


def path_prefix(page: Path) -> str:
    return '../' if len(page.relative_to(DOCS).parts) > 1 else ''


def attach_navigation(text: str, root: str) -> str:
    link = f'{root}operations.html'
    if f'href="{link}"' in text or f"href='{link}'" in text:
        return text
    marker = re.compile(r'(<a\s+href=[\'\"]' + re.escape(root) + r'templates\.html[\'\"][^>]*>)')
    return marker.sub(f'<a href="{link}">实验室</a>\\1', text, count=1)


def build_html() -> str:
    index = (DOCS / 'index.html').read_text(encoding='utf-8')
    marker = re.search(r'<main\s+id=[\'"]content[\'"]\s*>', index)
    if marker is None or '</main>' not in index[marker.end():]:
        raise RuntimeError('Expected site HTML layout unavailable')
    open_main = '<main id="content">'
    head = index[:marker.start()]
    tail = index[marker.end():].split('</main>', 1)[1]
    head = re.sub(r'<title>.*?</title>', '<title>GEO 实验室｜可复核的 AI 搜索验证 · GEO Handbook</title>', head, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="六个可执行的 GEO 验证实验，包含基线、技术检查、答案采样、最小改动和复测。">', head, count=1)
    head = head.replace('geo-handbook/index.html', 'geo-handbook/operations.html')
    head = head.replace('</head>', '<link rel="stylesheet" href="assets/evidence-lab.css"></head>', 1)
    head = attach_navigation(head, '')
    cards = []
    for x in EXPERIMENTS:
        steps = ''.join('<li>' + h(s) + '</li>' for s in x['steps'])
        cards.append(f'''<article class="el-card" id="{x['id'].lower()}">
          <div class="el-id">实验 {x['id']} <span>{h(x['time'])}</span></div>
          <h2>{h(x['name'])}</h2><p>{h(x['intro'])}</p>
          <ol>{steps}</ol>
          <div class="el-exit"><b>通过标准</b><span>{h(x['pass'])}</span></div>
          <a href="downloads/operations/{h(x['asset'])}" download>下载本实验表格 ↗</a>
        </article>''')
    body = f'''<section class="el-hero"><div class="container">
      <div class="eyebrow">GEO EVIDENCE LAB · REPRODUCIBLE EXPERIMENTS</div>
      <h1>用一轮真实实验，<br>验证一个 GEO 判断。</h1>
      <p>选一个真实客户问题，记录改动前的答案，修好一页内容，再按同样条件复测。把猜测与可核验的证据分开。</p>
      <div class="actions"><a class="btn" href="#e01">开始第一个实验</a><a class="btn alt" href="#protocol">生成实验记录卡</a></div>
      <div class="el-stats"><span>6 项独立实验</span><span>6 套可编辑表格</span><span>全程保留失败记录</span></div>
      </div></section>
      <section class="container el-section"><div class="el-header"><div class="eyebrow">METHOD</div>
      <h2>先定条件。再动页面。最后再判断。</h2>
      <p>六个实验按照证据形成的顺序排列。每一项都有具体操作、可下载模板和验收条件。</p></div>
      <div class="el-grid">{''.join(cards)}</div></section>
      <section class="container el-protocol" id="protocol">
      <div class="eyebrow">LOCAL TOOL · EXPERIMENT CARD</div>
      <h2>生成一张能复核的实验记录卡。</h2>
      <p>下面的信息只在浏览器本地生成，不提交服务器。先写好对照条件，避免做完才挑选有利的样本。</p>
      <div class="el-form">
        <label>客户的原始问题 <input id="lab-question" maxlength="240" placeholder="例：企业如何判断 GEO 项目是否有效？"></label>
        <label>要修改的页面 <input id="lab-url" maxlength="300" placeholder="https://example.com/guide"></label>
        <label>比较平台 <select id="lab-platform"><option>ChatGPT Search</option><option>Google AI 搜索</option><option>Bing / Copilot</option><option>其他平台</option></select></label>
        <label>基线观察日期 <input id="lab-baseline" type="date"></label>
        <label>复测日期 <input id="lab-after" type="date"></label>
        <label>实验编号 <input id="lab-id" maxlength="32" placeholder="GEO-EXP-001"></label>
      </div>
      <div class="actions"><button class="btn" id="lab-generate" type="button">生成记录卡</button><button class="btn alt" type="button" id="lab-copy">复制记录卡</button></div>
      <pre id="lab-output" class="el-output" role="status" aria-live="polite">填写上面的条件后生成。</pre>
      <p class="el-disclaimer">没有有效的改动前记录，就不能把改动后的差异说成已验证的效果。不同模型、账号、地区和日期的结果不可直接合并比较。</p>
      </section>
      <section class="container el-references"><h2>核验标准来自哪里？</h2>
      <p>网站可访问性、爬虫类型和引用监测应优先使用平台官方公开文档，不采用未经验证的「排名捷径」。</p>
      <div><a href="https://developers.google.com/search/docs/fundamentals/ai-optimization-guide" rel="noopener" target="_blank">Google Search Central · AI 搜索基础</a>
      <a href="https://developers.openai.com/api/docs/bots" rel="noopener" target="_blank">OpenAI · Crawlers</a>
      <a href="https://www.bing.com/webmasters" rel="noopener" target="_blank">Bing Webmaster Tools</a></div>
      </section>'''
    script = '''<script>(function(){"use strict";const $=id=>document.getElementById(id);let output="";$("lab-generate").addEventListener("click",function(){const q=$("lab-question").value.trim(),u=$("lab-url").value.trim(),b=$("lab-baseline").value,a=$("lab-after").value,id=$("lab-id").value.trim()||"未编号";if(!q||!u||!b||!a){$("lab-output").textContent="请填写客户问题、目标页面和两个观察日期。";return}if(a<b){$("lab-output").textContent="复测日期不能早于基线日期。";return}if(!/^https?:\\/\\/[^\\s]+$/i.test(u)){$("lab-output").textContent="目标页面需要是完整的 HTTP(S) URL。";return}output=["实验编号："+id,"客户真实问题："+q,"目标页面："+u,"观察平台："+$("lab-platform").value,"基线日期："+b,"复测日期："+a,"准备记录：固定问题文本、地区、账号状态、搜索触发与回答原文","修改记录：保存网页版本及改动说明","验收规则：只在同条件有效样本中比较，展示分子分母和失败样本","允许结论：仅报告观察结果；无法排除其他影响时不得声称因果"].join("\\n");$("lab-output").textContent=output});$("lab-copy").addEventListener("click",async function(){if(!output)return;try{await navigator.clipboard.writeText(output);this.textContent="已复制"}catch{$("lab-output").textContent=output+"\\n请手动复制上方内容。"}})})();</script>'''
    return head + open_main + body + '</main>' + tail.replace('</body>', script + '</body>', 1)


def build() -> None:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    # The previous collection has been replaced. Do not ship stale exported worksheets.
    for old in DOWNLOADS.glob('*.csv'):
        old.unlink()
    for source in sorted(SOURCE.glob('*.csv')):
        shutil.copyfile(source, DOWNLOADS / source.name)
    (DOCS / 'assets' / 'evidence-lab.css').write_text('''
.el-hero{padding:90px 0 72px;background:linear-gradient(180deg,#fff,#f8f8fa)}
.el-hero h1{font-size:clamp(38px,6vw,70px);letter-spacing:-.058em;line-height:1.12;margin:16px 0 18px;max-width:940px}
.el-hero p{font-size:19px;color:#6e6e73;max-width:780px}
.el-stats{display:flex;flex-wrap:wrap;gap:12px;margin-top:32px}
.el-stats span{font-size:13px;border:1px solid #e9e9ed;background:#fff;border-radius:99px;padding:8px 14px}
.el-section{padding-top:76px;padding-bottom:70px}
.el-header{max-width:780px;margin-bottom:32px}
.el-header h2,.el-protocol h2{letter-spacing:-.05em;line-height:1.16;font-size:clamp(30px,4vw,50px);margin:10px 0 15px}
.el-header p,.el-protocol p{font-size:16px;color:#6e6e73}
.el-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.el-card{border:1px solid #e8e8ed;background:#fff;box-shadow:0 7px 32px rgba(0,0,0,.035);border-radius:28px;padding:30px}
.el-id{color:#767680;font-size:12px;font-weight:700;letter-spacing:.07em}.el-id span{float:right;letter-spacing:0}
.el-card h2{font-size:25px;line-height:1.25;letter-spacing:-.04em;margin:14px 0 12px}.el-card p{font-size:15px;color:#6e6e73}
.el-card ol{padding-left:20px;margin-top:22px}.el-card li{font-size:14px;line-height:1.7;margin:8px 0}
.el-exit{border-top:1px solid #ececf0;margin-top:18px;padding:15px 0;display:grid;gap:5px}.el-exit b{font-size:12px}.el-exit span{font-size:13px;color:#6e6e73}
.el-card a{display:inline-block;font-size:13px;font-weight:700;text-decoration:underline;text-underline-offset:4px}
.el-protocol{margin-top:18px;margin-bottom:72px;background:#f7f7f9;border-radius:34px;padding-top:44px;padding-bottom:44px}
.el-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:25px}
.el-form label{display:block;font-size:13px;font-weight:600}.el-form input,.el-form select{display:block;margin-top:7px;width:100%;min-width:0;min-height:45px;padding:10px 12px;border-radius:13px;background:#fff;border:1px solid #dcdce2;color:#1d1d1f}
.el-output{white-space:pre-wrap;background:#1b1b1e;color:#fff;border-radius:20px;min-height:120px;margin-top:22px;padding:24px;overflow-wrap:anywhere}
.el-disclaimer{font-size:13px!important;margin-top:16px}
.el-references{padding-bottom:80px}.el-references h2{font-size:28px;letter-spacing:-.04em}.el-references p{color:#6e6e73}.el-references div{display:flex;flex-wrap:wrap;gap:14px}.el-references a{color:#1d1d1f;text-decoration:underline;font-size:13px}
@media(max-width:800px){.el-grid{grid-template-columns:1fr}}
@media(max-width:600px){.el-hero{padding:55px 0 46px}.el-hero h1{font-size:38px}.el-hero p{font-size:16px}.el-section{padding-top:50px}.el-card{padding:23px}.el-protocol{border-radius:24px;padding:24px 18px}.el-form{grid-template-columns:1fr}}
''', encoding='utf-8')
    (DOCS / 'operations.html').write_text(build_html(), encoding='utf-8')
    for page in sorted(DOCS.rglob('*.html')):
        if 'downloads' in page.parts or page.name == 'operations.html':
            continue
        original = page.read_text(encoding='utf-8')
        updated = attach_navigation(original, path_prefix(page))
        if page.name == 'index.html' and 'id="evidence-lab-entry"' not in updated:
            feature = '''<section class="section" id="evidence-lab-entry"><div class="container"><div class="eyebrow">EVIDENCE LAB</div><h2>用可复核的实验，而不是猜测，优化 GEO。</h2><p class="intro">六个操作实验、六套记录表格、一个本地实验卡生成器。从真实用户问题到技术检查、基线采样、内容改动与复测。</p><div class="actions"><a class="btn" href="operations.html">进入 GEO 实验室 →</a></div></div></section>'''
            updated = updated.replace('</main>', feature + '</main>', 1)
        if updated != original:
            page.write_text(updated, encoding='utf-8')
    sitemap = DOCS / 'sitemap.xml'
    xml = sitemap.read_text(encoding='utf-8')
    url = BASE_URL + 'operations.html'
    if url not in xml:
        xml = xml.replace('</urlset>', f'<url><loc>{url}</loc></url>\n</urlset>')
        sitemap.write_text(xml, encoding='utf-8')
    print('Built six reproducible GEO experiments, source templates and website entry points.')


if __name__ == '__main__':
    build()
