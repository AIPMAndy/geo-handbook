#!/usr/bin/env python3
"""Optional UI component smoke via Chromium set_content (navigation restricted in this environment)."""
import asyncio,re
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'docs'
CSS=(D/'assets/style.css').read_text(encoding='utf-8').split('\n',1)[1]
JS=(D/'assets/app.js').read_text(encoding='utf-8')
async def load(page,rel):
    raw=(D/rel).read_text(encoding='utf-8')
    raw=re.sub(r'<link rel="stylesheet"[^>]+>', '', raw)
    raw=re.sub(r'<script defer src="[^"]+"></script>', '', raw)
    await page.set_content(raw,wait_until='domcontentloaded')
    await page.add_style_tag(content=CSS)
    # A stub is needed: about:blank pages cannot use native localStorage.
    await page.evaluate('''() => { if (!window.__geoStore) window.__geoStore = {};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:(k)=>window.__geoStore[k]??null,
        setItem:(k,v)=>{window.__geoStore[k]=String(v)}
      }}) }''')
    await page.add_script_tag(content=JS)
async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width,height,mobile in [(1440,900,False),(390,844,True)]:
            ctx=await browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=mobile,has_touch=mobile,accept_downloads=True)
            page=await ctx.new_page()
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            await load(page,'index.html')
            await page.screenshot(path=str(ROOT/f'preview-{width}.png'),full_page=True)
            assert await page.locator('h1').count()==1
            assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2'),f'horizontal overflow on {width}'
            await load(page,'handbook.html')
            assert await page.locator('[data-lesson-card]').count()==26
            await page.locator('#lessonSearch').fill('ChatGPT')
            assert await page.locator('[data-lesson-card]:not(.hide)').count()>=1
            await load(page,'lessons/01.html')
            await page.locator('[data-complete]').click()
            assert '已完成' in await page.locator('[data-complete]').inner_text()
            await load(page,'30days.html')
            await page.locator('[data-day="01"]').check()
            assert '1 / 30' in await page.locator('#dayCount').inner_text()
            await load(page,'tools.html')
            await page.locator('#query').fill('某企业如何找 GEO 服务商？')
            await page.locator('#mention').select_option('yes')
            await page.locator('#citation').select_option('yes')
            await page.locator('#url').fill('https://example.com/service')
            await page.locator('button[type=submit]').click()
            assert '100.0%' in await page.locator('#logMention').inner_text()
            assert '100.0%' in await page.locator('#logCitation').inner_text()
            async with page.expect_download() as download_info:await page.locator('#exportCsv').click()
            dl=await download_info.value
            assert dl.suggested_filename=='geo-visibility-log.csv'
            assert not errors,f'JS errors on {width}: {errors}'
            print(f'BROWSER PASS (injected DOM): {width}px; search, progress, lesson, log, CSV')
            await ctx.close()
        await browser.close()
if __name__=='__main__':asyncio.run(main())
