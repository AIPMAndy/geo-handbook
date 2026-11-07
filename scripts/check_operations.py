#!/usr/bin/env python3
"""Red-team and deduplication gate for the additional GEO operations playbook."""
from __future__ import annotations
import csv
import re
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
REQUIRED=['brand-facts.csv','question-priority.csv','answer-samples.csv',
          'correction-queue.csv','channel-decisions.csv','review-ownership.csv',
          'measurement-dictionary.csv','handover-checklist.csv']
ERRORS=[]
class Inspector(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.headings=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='h1':self.headings.append(tag)

def insist(ok,msg):
    if not ok:ERRORS.append(msg)

def main():
    p=DOCS/'operations.html'
    insist(p.exists(),'企业实操入口缺失')
    source=p.read_text(encoding='utf-8') if p.exists() else ''
    insist(source.count('id="step-')==8,'八大实操模块不完整或重复')
    insist(source.count('class="ops-link"')==8,'实操下载入口数量不正确')
    insist('id="scoreBtn"' in source,'优先级工具不可见')
    insist('textContent=last' in source,'优先级结果缺少安全文本输出')
    insist('id="scoreResult"' in source,'得分反馈区域缺失')
    insist('metaver.vip' in source and 'AIPMAndy' in source,'作者官网和联系入口缺失')
    pages=[x for x in DOCS.rglob('*.html') if 'downloads' not in x.parts]
    insist(len(pages)==61,f'页面数异常，预期 61，实际 {len(pages)}')
    for f in pages:
        s=f.read_text(encoding='utf-8'); parser=Inspector();parser.feed(s)
        insist(len(parser.headings)==1,f'{f} h1 必须唯一')
        if f.name!='operations.html':
            root='../' if len(f.relative_to(DOCS).parts)>1 else ''
            path=root+'operations.html'
            insist(s.count('href="'+path+'"')>=1,f'{f} 缺少实操入口')
        for link in parser.links:
            if link.startswith(('https:','http:','mailto:','tel:','#')):continue
            link=link.split('#')[0].split('?')[0]
            if link:insist((f.parent/link).resolve().is_file(),f'失效内部链接 {f.relative_to(DOCS)} -> {link}')
    sitemap=(DOCS/'sitemap.xml').read_text(encoding='utf-8')
    insist(sitemap.count('<loc>')==61,'网站地图缺失新增页面或出现重复')
    assert (DOCS/'assets/operations.css').exists()
    for name in REQUIRED:
        f=ROOT/'operations'/name;target=DOCS/'downloads'/'operations'/name
        insist(f.exists() and target.exists(),f'模板缺失 {name}')
        if not f.exists():continue
        with f.open(newline='',encoding='utf-8-sig') as inp:rows=list(csv.DictReader(inp))
        insist(bool(rows),f'模板无示例 {name}')
        if rows:
            key=list(rows[0].keys())[0]
            ids=[r.get(key,'').strip() for r in rows]
            insist(len(ids)==len(set(ids)),f'模板键重复 {name}')
            insist(not any(not x for x in ids),f'模板主键缺失 {name}')
    # Respect user privacy: no unsanctioned attribution / personal profile links
    # in newly authored public assets. Official product documentation is permitted.
    newly_authored=[ROOT/'operations/README.md',ROOT/'operations/quality-gate.md',
                    ROOT/'scripts/build_operations.py',p]
    for f in newly_authored:
        s=f.read_text(encoding='utf-8')
        insist(not re.search(r'(?:twitter\.com|x\.com)/[^/\s]+/(?:status|statuses)/',s,re.I),
               f'{f} 包含未审查的社交媒体原帖地址')
        insist(not re.search(r'(?i)(?:第三方|外部)\s*(?:作者|账号)\s*[:：]\s*\S+',s),
               f'{f} 包含外部账号标识')
    if ERRORS:
        print('OPERATIONS QA FAILED')
        for e in ERRORS:print('-',e)
        raise SystemExit(1)
    print(f'PASS: 8 independent modules, 8 editable CSVs, 61 webpages, links, sitemap, privacy gate, dedupe and interactive score wiring.')

if __name__=='__main__':main()
