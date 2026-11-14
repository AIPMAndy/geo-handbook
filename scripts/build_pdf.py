#!/usr/bin/env python3
"""Publish the GEO handbook PDF from the same tracked Markdown used by the site.

No client result, AI ranking, or invented outcome is inserted by this publisher.
Every chapter links to its public, versioned source path on GitHub.
"""
from __future__ import annotations

from datetime import date
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import posixpath
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "pdf" / "geo-handbook-guide.pdf"
ONLINE = ROOT / "docs" / "downloads" / "geo-handbook-guide.pdf"
EDITION = ROOT / "pdf" / "edition.json"
REPO_URL = "https://github.com/AIPMAndy/geo-handbook/blob/main/"
BASE_URL = "https://aipmandy.github.io/geo-handbook/"

SOURCES = [
    ("01", "GEO 核心课程 · 26 章", sorted((ROOT / "chapters").glob("[0-9][0-9].md"))),
    ("02", "保姆级操作实验 · 16 项", sorted((ROOT / "labs").glob("[0-9][0-9].md"))),
    ("03", "行业场景 · 6 个教学模拟", sorted((ROOT / "cases").glob("[0-9][0-9].md"))),
    ("04", "业务实施手册", sorted((ROOT / "playbooks").glob("[0-9][0-9]-*.md"))),
    ("05", "方法、证据与审计边界", [
        ROOT / "GEO_OPERATING_MANUAL.md",
        ROOT / "EDITORIAL_STANDARDS.md",
        ROOT / "PROMPT_LIBRARY.md",
        ROOT / "operations" / "README.md",
    ]),
]

STYLE = r"""
@page {size:A4;margin:20mm 18mm 19mm;
  @top-left{content:"AI CHIEF ANDY / GEO FIELD GUIDE";font:8pt "Noto Sans CJK SC";letter-spacing:.08em;color:#63748a}
  @top-right{content:string(chapter);font:8pt "Noto Sans CJK SC";color:#748293}
  @bottom-left{content:"星觉科技 · 微信 AIPMAndy";font:8pt "Noto Sans CJK SC";color:#63748a}
  @bottom-right{content:counter(page);font:8pt "Noto Sans CJK SC";color:#63748a}}
@page:first{margin:0;@top-left{content:none}@top-right{content:none}@bottom-left{content:none}@bottom-right{content:none}}
*{box-sizing:border-box}
html{font-family:"Noto Sans CJK SC","Noto Sans SC",sans-serif;font-size:9.5pt;color:#182636}
body{margin:0;line-height:1.7}
h1,h2,h3,h4{line-height:1.3;color:#14263b;break-after:avoid}
h1{font-size:20pt}h2{font-size:14.5pt;margin:7mm 0 3mm}h3{font-size:11pt;margin:5mm 0 2mm}
p{orphans:3;widows:3;margin:2mm 0 3mm}li{margin:1.4mm 0;orphans:2;widows:2}
ul,ol{padding-left:6mm}
a{color:#20588b;text-decoration:none;overflow-wrap:anywhere}
pre{background:#182538;color:#eef4fa;border-radius:2mm;padding:4mm;white-space:pre-wrap;overflow-wrap:anywhere;font:7.5pt/1.6 monospace}
code{background:#edf2f7;overflow-wrap:anywhere;font:8pt monospace;padding:.3mm .8mm}
pre code{background:transparent;color:inherit}
blockquote{border-left:3px solid #406f9e;background:#eef4f8;padding:4mm 5mm;margin:4mm 0}
table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:8pt}
td,th{border:1px solid #dce5ed;padding:2mm;overflow-wrap:anywhere;vertical-align:top}
th{background:#edf3f9}
hr{border:0;border-top:1px solid #d7e1ea;margin:6mm 0}
.cover{height:297mm;background:#101d2f;color:#fff;padding:35mm 25mm 24mm;page-break-after:always;position:relative}
.cover .eyebrow{color:#aecce9;letter-spacing:.17em;font-size:10pt}
.cover h1{font-size:40pt;color:#fff;line-height:1.16;margin:24mm 0 12mm;letter-spacing:-.045em}
.cover .subtitle{font-size:15pt;color:#cbd9e8;max-width:155mm;line-height:1.7}
.cover .bar{width:100%;height:1px;background:#61768c;margin:25mm 0 11mm}
.cover .facts{font-size:11pt;line-height:2;color:#c7d5e5}
.cover .imprint{position:absolute;bottom:23mm;left:25mm;font-size:10pt;line-height:1.95;color:#d4e1ee}
.intro{page-break-after:always}
.intro .eyebrow,.part .eyebrow,.chapter .eyebrow{color:#2d679e;letter-spacing:.13em;font-size:8pt;font-weight:700}
.intro h2{font-size:25pt;margin:6mm 0}
.notice{background:#eff4f8;border-left:3px solid #3f719e;padding:5mm 6mm;margin:5mm 0}
.toc{margin:8mm 0}
.toc-part{margin:5mm 0;break-inside:avoid}
.toc-part h3{margin:2mm 0;font-size:12pt}
.toc-row{border-bottom:1px solid #dde5ed;padding:1.1mm 0;font-size:8.7pt}
.toc-row a{display:block;color:#294d74}
.toc-row a:after{content:target-counter(attr(href),page);float:right;color:#8290a0}
.part{page-break-before:always;padding-top:40mm}
.part h2{font-size:29pt;line-height:1.2}
.part p{font-size:11pt;color:#66788b}
.chapter{page-break-before:always}
.chapter .head{border-bottom:1px solid #d9e2eb;padding:0 0 4mm;margin-bottom:6mm}
.chapter .head h2{font-size:19pt;margin:2mm 0;string-set:chapter content()}
.chapter .head p{font-size:8.4pt;color:#68788d}
.chapter .body h1{font-size:15.5pt}
.chapter .body h2{font-size:13.5pt}
.chapter .body h3{font-size:11pt}
.chapter .body img{max-width:100%;height:auto}
.provenance{font-size:8.3pt;background:#f1f4f8;padding:3mm;border-radius:2mm;overflow-wrap:anywhere}
.contact{page-break-before:always;min-height:230mm;background:#101d2f;color:white;padding:29mm 22mm}
.contact h2{font-size:29pt;color:white;margin:8mm 0}
.contact p{font-size:11pt;color:#ccd9e7}
.contact li{border-bottom:1px solid #49617b;padding:4mm 0;list-style:none}
.contact ul{padding:0;margin:14mm 0}
.contact a{color:#c2dfff}
.contact .legal{font-size:9pt;color:#b4c4d3;margin-top:21mm}
"""


def escape(s: object) -> str:
    return html.escape(str(s), quote=True)


def title_for(path: Path) -> str:
    match = re.search(r"^#\s+(.+)$", path.read_text(encoding="utf-8"), re.M)
    return match.group(1).strip() if match else path.stem


def normalize_relative_links(markdown_text: str, path: Path) -> str:
    """Make repo-relative Markdown links stay useful in the standalone PDF."""
    def replace(match):
        label, target = match.group(1), match.group(2)
        if urlsplit(target).scheme or target.startswith(("#", "mailto:")):
            return match.group(0)
        p = posixpath.normpath(posixpath.join(path.relative_to(ROOT).parent.as_posix(), target))
        if p.startswith("../") or p == "..":
            return match.group(0)
        return f"[{label}]({REPO_URL}{p})"
    return re.sub(r"(?<!!)\[([^\]\n]+)\]\(([^)\s]+)\)", replace, markdown_text)


def fingerprint(paths: list[Path]) -> str:
    digest = sha256(Path(__file__).read_bytes())
    for p in sorted(set(paths)):
        digest.update(p.relative_to(ROOT).as_posix().encode())
        digest.update(p.read_bytes())
    return digest.hexdigest()


def build() -> None:
    import markdown
    from weasyprint import HTML

    all_paths = [p for _, _, group in SOURCES for p in group]
    expected = [26, 16, 6, 4, 4]
    actual = [len(group) for _, _, group in SOURCES]
    if actual != expected:
        raise ValueError(f"Source groups changed: expected {expected}, found {actual}")
    if any(not p.is_file() for p in all_paths):
        raise FileNotFoundError("One or more canonical Markdown files are missing")
    source_hash = fingerprint(all_paths)
    if PDF.exists() and EDITION.exists():
        try:
            edition = json.loads(EDITION.read_text(encoding="utf-8"))
            if edition.get("source_sha256") == source_hash and PDF.stat().st_size > 40000:
                ONLINE.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PDF, ONLINE)
                print("Reused current PDF:", PDF, "source_sha256:", source_hash)
                return
        except (ValueError, OSError):
            pass

    toc, sections = [], []
    for number, group_title, group in SOURCES:
        toc.append(f'<div class="toc-part"><h3>{escape(number)} / {escape(group_title)}</h3>')
        sections.append(f'<section class="part"><div class="eyebrow">PART {escape(number)}</div><h2>{escape(group_title)}</h2><p>来自 GitHub 公开源文档，按章节保留可复核内容与链接。</p></section>')
        for i, path in enumerate(group, 1):
            relative = path.relative_to(ROOT).as_posix()
            key = f"chapter-{number}-{i:02d}"
            title = title_for(path)
            toc.append(f'<div class="toc-row"><a href="#{key}">{escape(title)}</a></div>')
            raw = path.read_text(encoding="utf-8")
            raw = re.sub(r"^#\s+[^\n]+\n?", "", raw, count=1)
            body = markdown.markdown(normalize_relative_links(raw, path), extensions=("tables", "fenced_code", "sane_lists"))
            sections.append(f'<section class="chapter" id="{key}"><div class="head"><div class="eyebrow">PART {number} · {i:02d}</div><h2>{escape(title)}</h2><p>原始文件：<a href="{REPO_URL}{escape(relative)}">{escape(relative)}</a></p></div><div class="body">{body}</div><p class="provenance">来源：公开仓库 <a href="{REPO_URL}{escape(relative)}">{escape(relative)}</a>。内容随仓库迭代；本版为出版快照。所有示例和演练如无公开原始证据均不代表真实客户结果。</p></section>')
        toc.append("</div>")
    publication = date.today().isoformat()
    cover = f"""<section class="cover"><div class="eyebrow">XINGJUE KNOWLEDGE SERIES / GEO HANDBOOK</div><h1>GEO<br>生成式 AI 搜索<br>实操手册</h1><p class="subtitle">不是“保证 AI 推荐”的话术。把真实问题、来源证据、页面建设、实验监测与企业交付做成可复现的工作流。</p><div class="bar"></div><p class="facts">26 章核心课程 · 16 个动手实验<br>6 个明确标注的教学模拟 · 25 套可编辑模板<br>30 天执行计划与企业交付方法</p><p class="imprint">AI 酋长 Andy / 星觉科技<br>微信 AIPMAndy<br>https://metaver.vip/ · https://www.a6no1.cn/<br>开源 · 不承诺 AI 排名、流量或收入 · {publication}</p></section>"""
    intro = f"""<section class="intro"><div class="eyebrow">START HERE / HOW TO USE</div><h2>先做真实的事。<br>再衡量真实的结果。</h2><div class="notice"><b>阅读路径：</b>先看 26 章建立体系，再从 16 个实验中选择可复现任务，最后使用行业演练和企业交付模板。<br><b>数字边界：</b>“AI 提及”“AI 引用”“站点访问”“付费咨询”是不同指标，必须分别留存证据。</div><p>本出版物由仓库中 Markdown 原文自动生成。所有假设场景和合成数据都只是教学演练，不代表作者服务的真实客户、成交、排名或收益。平台规定可能变化，以各官方现行文档为准。</p><p>可运行的 HTML 检查、CSV 数据分析与监测记录工具请使用 <a href="{BASE_URL}">交互式网站</a>；可编辑模板请到 <a href="{BASE_URL}templates.html">模板下载页面</a>。</p><p>作者：AI 酋长 Andy · 出版快照 {publication} · <a href="https://metaver.vip/services">咨询与合作</a></p><h2>目录</h2><div class="toc">{''.join(toc)}</div></section>"""
    contact = f"""<section class="contact" id="author-contact"><div class="eyebrow">AI CHIEF ANDY / XINGJUE TECHNOLOGY</div><h2>从内容，<br>走向可核验的交付。</h2><p>本手册和网页工具免费开放；企业 GEO 实施、技术与内容审查、AI 产品咨询，可从官网了解服务范围。</p><ul><li>个人微信：<b>AIPMAndy</b></li><li>个人官网：<a href="https://metaver.vip/">https://metaver.vip/</a></li><li>公司官网：<a href="https://www.a6no1.cn/">https://www.a6no1.cn/</a></li><li>服务入口：<a href="https://metaver.vip/services">https://metaver.vip/services</a></li><li>网站与工具：<a href="{BASE_URL}">{BASE_URL}</a></li><li>GitHub 源码：<a href="https://github.com/AIPMAndy/geo-handbook">AIPMAndy/geo-handbook</a></li></ul><p class="legal">不保证被 AI 搜索收录、推荐或获得任何排名、询盘和收入。所有官方规则以最新原始链接为准。演练并非客户成功案例。</p></section>"""
    output = '<html lang="zh-CN"><head><meta charset="utf-8"><title>GEO 生成式 AI 搜索实操手册</title><style>'+STYLE+'</style></head><body>'+cover+intro+''.join(sections)+contact+'</body></html>'
    PDF.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=output, base_url=str(ROOT)).write_pdf(PDF)
    if PDF.read_bytes()[:4] != b"%PDF" or PDF.stat().st_size < 40000:
        raise RuntimeError("Publication PDF is empty or invalid")
    ONLINE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PDF, ONLINE)
    EDITION.write_text(json.dumps({"source_sha256": source_hash, "publication": publication, "chapters": 26, "tasks": 16, "cases": 6, "canonical_source_count": len(all_paths)}, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"Published {PDF.stat().st_size} bytes, {len(all_paths)} source files, fingerprint {source_hash}")


if __name__ == "__main__":
    build()
