#!/usr/bin/env python3
"""Offline GEO/SEO *structure* audit for a local HTML snapshot.

Does not crawl the site, interpret robots, prove indexing, or predict AI citations.
Standard library only. Do not process untrusted huge HTML; max 2 MiB by default.
"""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse

class HTMLAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_depth=0;self.in_main=0;self.in_script=0;self.in_style=0;self.active_jsonld=False;self.in_body=False
        self.title=[];self.meta={};self.headings=[];self.links=[];self.canonical=[]
        self.visible=[];self.scripts=[];self.images=[];self.current_heading=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title':self.title_depth+=1
        if tag=='main':self.in_main+=1
        if tag=='body':self.in_body=True
        if tag=='script':
            self.in_script+=1
            self.active_jsonld=(a.get('type','').lower()=='application/ld+json')
            if self.active_jsonld:self.scripts.append([])
        if tag=='style':self.in_style+=1
        if tag=='meta':
            for key in ['name','property','http-equiv']:
                if a.get(key):self.meta[a[key].lower()]=a.get('content','')
        if tag=='link' and 'canonical' in a.get('rel','').lower().split():self.canonical.append(a.get('href',''))
        if tag in ['h1','h2','h3']:
            self.current_heading=[tag,[]]
            self.headings.append(self.current_heading)
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='img':self.images.append(a)
    def handle_endtag(self,tag):
        if tag=='title':self.title_depth=max(0,self.title_depth-1)
        if tag=='main':self.in_main=max(0,self.in_main-1)
        if tag=='script':self.in_script=max(0,self.in_script-1);self.active_jsonld=False
        if tag=='style':self.in_style=max(0,self.in_style-1)
        if tag in ['h1','h2','h3']:self.current_heading=None
    def handle_data(self,data):
        if self.title_depth:self.title.append(data)
        if self.current_heading:self.current_heading[1].append(data)
        if self.in_script:
            if self.active_jsonld and self.scripts:self.scripts[-1].append(data)
            return
        if not self.in_style and self.in_body:self.visible.append(data)

def audit_html(source:str,canonical_url:str='')->dict:
    p=HTMLAudit();p.feed(source)
    headings=[{'level':level,'text':' '.join(data).strip()} for level,data in p.headings]
    h1=[h for h in headings if h['level']=='h1']
    title=' '.join(p.title).strip()
    desc=p.meta.get('description','').strip()
    robots=p.meta.get('robots','').lower()
    canonical=p.canonical[0] if p.canonical else ''
    text=' '.join(p.visible)
    text=' '.join(text.split())
    issues=[]
    def add(code,severity,observation,action):issues.append({'code':code,'severity':severity,'observation':observation,'action':action})
    if not title:add('missing_title','high','页面源 HTML 没有非空 <title>','添加唯一、准确的页面标题')
    if len(h1)!=1:add('h1_count','medium',f'H1 数量 = {len(h1)}','一般建议有一个明确的页面主标题；先关注可读性')
    if not desc:add('missing_description','low','缺少 meta description','写清页面价值；它不是直接的 AI 引用开关')
    if not canonical:add('missing_canonical','medium','没有显式 canonical','为重要规范页考虑设置符合实际的 canonical')
    elif canonical_url and canonical.rstrip('/')!=canonical_url.rstrip('/'):
        add('canonical_mismatch','medium',f'声明 {canonical}；本次输入 URL {canonical_url}','核对是否有意规范到其他 URL')
    if re.search(r'(?:^|[\s,])noindex(?:[\s,]|$)',robots):add('noindex','critical',f'meta robots={robots}','若这是计划被搜索索引的公开页，审查并按站点策略修复')
    if len(text)<150:add('thin_visible_html','medium',f'源 HTML 可见文本约 {len(text)} 字符','确认服务器交付了有价值正文；不要仅追求字数')
    if any(not i.get('alt') for i in p.images):add('missing_image_alt','low','存在缺少 alt 的图片','给内容图片提供适合的 alt；装饰图可用空 alt 并核实用途')
    schemas=[]
    for raw in p.scripts:
        data=''.join(raw).strip()
        if not data:continue
        try:
            obj=json.loads(data)
            typ=obj.get('@type') if isinstance(obj,dict) else ('array' if isinstance(obj,list) else 'unknown')
            schemas.append({'valid_json':True,'type':typ})
        except json.JSONDecodeError as e:
            schemas.append({'valid_json':False,'error':str(e)})
            add('invalid_jsonld','medium',f'JSON-LD JSON 解析错误: {e}','按 JSON 语法修正；有效 JSON 不代表富媒体资格')
    return {'input_url':canonical_url,'title':title,'meta_description':desc,'headings':headings,'canonical':canonical,'meta_robots':robots,'html_visible_chars':len(text),'outgoing_links':len(p.links),'images':len(p.images),'jsonld':schemas,'issues':issues,'issue_count':len(issues),'assessment_scope':'只检查传入的静态 HTML；不检测 robots.txt、HTTP 状态、真实索引、AI 引用或网站整体表现'}

def main(argv=None):
    pa=argparse.ArgumentParser(description='GEO offline HTML structure audit (not live indexing or AI ranking)')
    pa.add_argument('--file',required=True,help='HTML 文件路径；必须是你有权限检查的网页')
    pa.add_argument('--url',default='',help='用于比较 canonical 的网页 URL，不会发出任何网络请求')
    pa.add_argument('--json',action='store_true',help='输出 JSON')
    a=pa.parse_args(argv)
    if a.url and (urlparse(a.url).scheme not in ('http','https') or not urlparse(a.url).netloc):pa.error('--url 必须是有效 http(s) URL')
    f=Path(a.file)
    if f.stat().st_size>2*1024*1024:pa.error('HTML 最大为 2 MiB，请缩小样本')
    r=audit_html(f.read_text(encoding='utf-8-sig',errors='replace'),a.url)
    if a.json:print(json.dumps(r,ensure_ascii=False,indent=2))
    else:
        print('HTML 结构诊断（离线，仅供初筛）')
        print('TITLE:',r['title'] or '（无）','| CANONICAL:',r['canonical'] or '（无）')
        print('HTML 正文字符:',r['html_visible_chars'],'| 风险提示:',r['issue_count'])
        for v in r['issues']:print(f"[{v['severity']}] {v['code']}: {v['observation']} → {v['action']}")
        print('边界:',r['assessment_scope'])
    return 0
if __name__=='__main__':sys.exit(main())
