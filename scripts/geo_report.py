#!/usr/bin/env python3
"""Offline manual GEO observation CSV report; no ranking/causality claims.

Reads local CSV from the browser tracker or examples. All samples are observational.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
from collections import defaultdict
FIELDS=['date','platform','region','phase','question_type','ai_answer_triggered','query','brand_mentioned','owned_url_cited','citation_url','evidence']

def yes(value):return str(value).strip().lower() in {'1','true','yes','y','是'}
def normalise(raw):
    r={k:str(raw.get(k,'')).strip() for k in FIELDS}
    r['question_type']=r['question_type'] or 'natural'
    r['phase']=r['phase'] or 'baseline'
    if r['owned_url_cited'] and yes(r['owned_url_cited']) and not r['citation_url']:
        r['flag']='引用标记是但缺少引用 URL，需人工核实'
    return r

def compute(rows):
    seen=[];excluded={'brand':0,'not_triggered':0};flagged=[]
    for raw in rows:
        r=normalise(raw)
        if r.get('flag'):flagged.append({'query':r['query'],'flag':r['flag']})
        if r['question_type']!='natural':excluded['brand']+=1;continue
        if not yes(r['ai_answer_triggered']):excluded['not_triggered']+=1;continue
        seen.append(r)
    groups=defaultdict(list)
    for r in seen:groups[(r['phase'],r['platform'],r['region'])].append(r)
    result=[]
    for (phase,platform,region),group in sorted(groups.items()):
        n=len(group);m=sum(yes(x['brand_mentioned']) for x in group)
        cited=sum(yes(x['owned_url_cited']) and bool(x['citation_url']) for x in group)
        result.append({'phase':phase,'platform':platform,'region':region,'valid_answers':n,'mentions':m,'mention_rate_pct':round(100*m/n,1),'citations':cited,'citation_rate_pct':round(100*cited/n,1)})
    return {'total_rows':len(rows),'excluded':excluded,'valid_samples':len(seen),'groups':result,'flags':flagged,'warning':'小样本手工观测；不是全平台概率，不保证同题可重现，前后变化不可单独证明因果'}

def main(argv=None):
    p=argparse.ArgumentParser(description='GEO local CSV report from manual test log')
    p.add_argument('csv_path',help='CSV（支持 UTF-8/UTF-8 BOM）；不联网、不上传数据')
    p.add_argument('--json',action='store_true')
    args=p.parse_args(argv)
    with Path(args.csv_path).open(encoding='utf-8-sig',newline='') as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames or any(x not in rd.fieldnames for x in FIELDS):
            p.error('缺少必填列；需要浏览器工具导出的 11 列格式。')
        rows=list(rd)
    out=compute(rows)
    if args.json:print(json.dumps(out,ensure_ascii=False,indent=2))
    else:
        print(f"导入 {out['total_rows']} 行，有效自然测试 {out['valid_samples']}；排除品牌直搜 {out['excluded']['brand']}，未触发 {out['excluded']['not_triggered']}。")
        for x in out['groups']:
            print(f"{x['phase']:8} | {x['platform']:<23} | {x['region']:<10} | 样本 {x['valid_answers']:3} | 提及 {x['mentions']:2} ({x['mention_rate_pct']}%) | 自有引用 {x['citations']:2} ({x['citation_rate_pct']}%)")
        for issue in out['flags']:print('核查:',issue['query'],issue['flag'])
        print('口径:',out['warning'])
    return 0
if __name__=='__main__':sys.exit(main())
