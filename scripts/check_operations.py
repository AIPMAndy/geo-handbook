#!/usr/bin/env python3
"""Independent release gate for the GEO evidence lab."""
from __future__ import annotations
import csv
import re
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
FILES = [
    '01-experiment-plan.csv', '02-page-readiness.csv', '03-answer-captures.csv',
    '04-change-ledger.csv', '05-review-decision.csv', '06-outcome-trace.csv',
]

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = 0
        self.links = []
    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        if tag == 'h1': self.headings += 1
        if tag == 'a' and at.get('href'): self.links.append(at['href'])

def test() -> None:
    errors = []
    def require(test, label):
        if not test: errors.append(label)
    source = (DOCS / 'operations.html').read_text(encoding='utf-8')
    require(source.count('class="el-card"') == 6, 'Exactly six experiment cards')
    require(source.count('下载本实验表格') == 6, 'Exactly six downloadable assets')
    require('id="lab-generate"' in source and 'textContent=output' in source, 'Interactive card generator safely renders text')
    require('https://metaver.vip/' in source, 'Creator website credit retained')
    for p in [ROOT / 'scripts/build_operations.py', ROOT / 'scripts/check_operations.py', ROOT / 'operations/README.md', ROOT / 'operations/quality-gate.md', DOCS / 'operations.html']:
        s = p.read_text(encoding='utf-8')
        require(not re.search(r'(?:x|twitter)\.com/[^\s]+/(?:status|statuses)/\d+',s,re.I), f'No embedded social original in {p.name}')
        if p.name != 'check_operations.py':
            require('iframe' not in s.lower() and 'fetch("https:' not in s, f'No embedded external reader in {p.name}')
    pages = [p for p in DOCS.rglob('*.html') if 'downloads' not in p.parts]
    require(len(pages) == 61, f'Expected 61 HTML pages, got {len(pages)}')
    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding='utf-8'))
        require(parser.headings == 1, f'Exactly one h1: {page}')
        if page.name != 'operations.html':
            prefix = '../' if len(page.relative_to(DOCS).parts)>1 else ''
            require(prefix+'operations.html' in parser.links, f'Navigation to lab: {page}')
        for link in parser.links:
            if link.startswith(('http:', 'https:', 'mailto:', 'tel:', '#')): continue
            plain = link.split('#')[0].split('?')[0]
            if plain: require((page.parent / plain).resolve().is_file(), f'Broken link: {page} -> {link}')
    for name in FILES:
        original = ROOT / 'operations' / name
        copied = DOCS / 'downloads' / 'operations' / name
        require(original.exists() and copied.exists(), f'Both CSVs available: {name}')
        if original.exists():
            with original.open(encoding='utf-8-sig', newline='') as f: rows = list(csv.DictReader(f))
            require(bool(rows), f'Non-empty CSV: {name}')
            require(all(str(v).startswith('DEMO-') for v in (r[next(iter(r))] for r in rows)), f'All examples marked DEMO: {name}')
    exported = sorted(p.name for p in (DOCS/'downloads'/'operations').glob('*.csv'))
    require(exported == sorted(FILES), 'No retired worksheet exports')
    xml = (DOCS / 'sitemap.xml').read_text(encoding='utf-8')
    require(xml.count('<loc>') == 61, 'Exactly 61 sitemap URLs')
    if errors:
        print('GEO EVIDENCE LAB RELEASE GATE FAILED')
        for e in errors: print('- ',e)
        raise SystemExit(1)
    print(f'PASS: {len(pages)} pages, {len(FILES)} new datasets, links, sitemap, independent experiments, text-safety checks.')

if __name__ == '__main__': test()
