#!/usr/bin/env python3
"""Adversarial static quality gate. No network required, no false live-index claims."""
import sys,re,html
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs';sys.path.insert(0,str(ROOT/'content'))
from chapters import CHAPTERS,DAYS,SOURCES
class Inspect(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.images=[];self.titles=0;self.body=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='img':self.images.append(a)
        if tag=='h1':self.titles+=1
    def handle_data(self,data):self.body.append(data)
errors=[]
def fail(x):errors.append(x)
if len(CHAPTERS)!=26:fail('课程必须有26章')
if len(DAYS)!=30:fail('逐日计划必须有30天')
if len(list((ROOT/'templates').iterdir()))!=25:fail('模板不是25个')
if len(list((ROOT/'playbooks').iterdir()))!=4:fail('行业路线不是4个')
if len({x[0] for x in CHAPTERS})!=len(CHAPTERS):fail('课程ID重复')
for x in CHAPTERS:
    if len(x[4])!=5:fail(f'{x[0]}章并非5步')
    if any(len(s)<13 for s in x[4]):fail(f'{x[0]}章步骤太空泛')
if len(SOURCES)<8:fail('官方来源不足')
for label,url,*_ in SOURCES:
    if not url.startswith('https://'):fail(f'官方来源地址无效: {label}')
expected=['index.html','handbook.html','30days.html','templates.html','tools.html','services.html','sources.html','labs.html','cases.html','diagnose.html','measure.html','pricing.html','sitemap.xml','robots.txt']
for p in expected:
    if not (D/p).is_file():fail(f'站点缺少 {p}')
for f in D.rglob('*.html'):
    if 'downloads' in f.relative_to(D).parts:continue  # teaching test fixtures are intentionally imperfect
    txt=f.read_text(encoding='utf-8');p=Inspect()
    try:p.feed(txt)
    except Exception as e:fail(f'HTML 解析失败: {f} {e}');continue
    if p.titles!=1:fail(f'{f.relative_to(D)} h1 数量 {p.titles}, 应为1')
    for link in p.links:
        if link.startswith(('http:','https:','mailto:','tel:','#')):continue
        normalized=link.split('?')[0].split('#')[0]
        if normalized and not (f.parent/normalized).resolve().is_file():fail(f'失效内链 {f.relative_to(D)} -> {link}')
    if 'AIPMAndy' not in txt:fail(f'{f.relative_to(D)} 丢失微信入口')
    if 'metaver.vip' not in txt:fail(f'{f.relative_to(D)} 丢失官网入口')
    if p.images and any(not a.get('alt') for a in p.images):fail(f'{f.relative_to(D)} 图片缺少 alt')
for f in (D/'lessons').glob('*.html'):
    txt=f.read_text(encoding='utf-8')
    for s in ['跟着做','交付与验收','失败模式','data-complete']:
        if s not in txt:fail(f'{f.name} 缺少关键元素 {s}')
if len(list((D/'lessons').glob('*.html')))!=26:fail('可访问的单章页面不是26篇')
if len(list((D/'labs').glob('*.html')))!=16:fail('可访问的实验页面不是16篇')
if len(list((D/'cases').glob('*.html')))!=6:fail('可访问的演练页面不是6篇')
if len([f for f in D.rglob('*.html') if 'downloads' not in f.parts])!=60:fail('正式站点页面数不是60篇')
for f in (ROOT/'labs').glob('*.md'):
    txt=f.read_text(encoding='utf-8')
    if len(txt)<1500 or '## 最终验收' not in txt or '## 常见失败' not in txt:fail(f'实操实验质量不够 {f.name}')
    if txt.count('**完成凭证：**')<5:fail(f'实操缺少可验证步骤 {f.name}')
for f in (ROOT/'cases').glob('*.md'):
    if '教学模拟' not in f.read_text(encoding='utf-8'):fail(f'模拟案例未明确标注 {f.name}')
if not (D/'assets/extras.js').exists():fail('浏览器额外工具 JS 不存在')
if 'labs/01.html' not in (D/'labs.html').read_text():fail('实操实验入口未正确生成')
if 'noindex' not in (D/'diagnose.html').read_text() and not (ROOT/'scripts/site_audit.py').exists():fail('HTML 检测工具未包含索引风险检查')
js=(D/'assets/app.js').read_text(encoding='utf-8')
for s in ['localStorage','exportCsv','visibilityForm','lessonSearch','dayCount']:
    if s not in js:fail(f'交互功能缺少 {s}')
# Avoid unsupported or manipulative guarantees in editorial content.
for f in list((ROOT/'chapters').glob('*.md'))+list((ROOT/'playbooks').glob('*.md')):
    txt=f.read_text(encoding='utf-8')
    for bad in ['保证登顶','保证上第一','保上首页','百分百推荐','一键控制AI排名']:
        if bad in txt:fail(f'高风险保证性表述: {f.name} {bad}')
if errors:
    print('QUALITY GATE FAILED:')
    for e in errors:print(' -',e)
    sys.exit(1)
print(f'PASS: 26 chapters + 16 labs + 6 cases + 30 days + 25 templates + 4 playbooks; {len([f for f in D.rglob("*.html") if "downloads" not in f.parts])} HTML pages, local links, sources, contact, interactive hooks.')
