#!/usr/bin/env python3
"""Optional Chromium smoke via in-memory DOM injection.

This environment blocks browser navigation, including intercepted test domains.
Tests visual layout and JS interactions, but NOT URLs, reload persistence, or public Pages.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs'

def load_page(page,filename):
    html=(D/filename).read_text(encoding='utf-8')
    css=(D/'assets/style.css').read_text(encoding='utf-8')
    app=(D/'assets/app.js').read_text(encoding='utf-8')
    extras=(D/'assets/extras.js').read_text(encoding='utf-8')
    # Inline all assets because browser cannot navigate to local/test URLs.
    css=css.split(';',1)[1] if css.lstrip().startswith('@import') else css
    html=html.replace('</head>','<style>'+css+'</style></head>').replace('</body>','<script>'+app+'</script><script>'+extras+'</script></body>')
    page.set_content(html,wait_until='domcontentloaded')

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        ctx=browser.new_context(viewport={'width':1440,'height':900},device_scale_factor=1)
        page=ctx.new_page()
        page.on('dialog',lambda dialog:dialog.accept())
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        load_page(page,'index.html')
        assert page.locator('h1').count()==1
        assert page.locator('a[href="labs.html"]').count()>=1
        page.screenshot(path=str(ROOT/'preview-v2-desktop.png'),full_page=True)
        for filename in ['index.html','handbook.html','labs/01.html','cases/01.html','measure.html','pricing.html']:
            load_page(page,filename)
            assert page.locator('h1').count()==1,filename
        print('PASS: 6 representative HTML DOM pages loaded (navigation not testable in sandbox)')
        load_page(page,'diagnose.html')
        page.locator('#loadBrokenHtml').click()
        page.locator('#runHtmlAudit').click()
        value=page.locator('#htmlAuditResults').inner_text()
        assert 'noindex' in value and 'title' in value,value
        print('PASS: HTML diagnostic detects deliberate noindex/title errors')
        load_page(page,'measure.html')
        page.locator('#loadDemoCsv').click()
        assert '合成样例' in page.locator('#csvResults').inner_text()
        page.locator('#reportCsv').set_input_files(str(ROOT/'examples/synthetic-visibility.csv'))
        page.wait_for_function("document.querySelector('#csvResults')?.innerText.includes('本地 CSV 分析结果')")
        assert '30' in page.locator('#csvResults').inner_text()
        print('PASS: CSV demo and imported CSV render client-side analysis')
        load_page(page,'pricing.html')
        page.locator('#quoteHours').fill('20');page.locator('#quoteHourly').fill('100')
        page.locator('#quoteOther').fill('500');page.locator('#quoteQa').fill('500')
        page.locator('#quoteMargin').fill('50');page.locator('#calculateQuote').click()
        value=page.locator('#quoteResult').inner_text()
        assert '¥6,000' in value,value
        print('PASS: quote calculator math driven by user inputs')
        load_page(page,'30days.html')
        page.locator('[data-day="01"]').check()
        assert '1 / 30' in page.locator('#dayCount').inner_text()
        print('PASS: 30 day progress changes after click (refresh persistence not testable)')
        load_page(page,'tools.html')
        page.locator('#query').fill('测试输入：不是品牌词')
        page.locator('#visibilityForm button[type="submit"]').click()
        assert page.locator('#logN').inner_text()=='1'
        print('PASS: manual monitoring form calculates effective sample')
        ctx.close()
        mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1)
        mp=mobile.new_page();load_page(mp,'index.html')
        assert mp.locator('h1').count()==1
        width=mp.evaluate('document.documentElement.scrollWidth')
        assert width<=392,f'mobile horizontal overflow {width}'
        mp.screenshot(path=str(ROOT/'preview-v2-mobile.png'),full_page=True)
        print('PASS: 390px mobile layout without horizontal overflow')
        mobile.close();browser.close()
        if errors:raise AssertionError('Browser JS errors: '+str(errors[:3]))
        print('PASS: no uncaught JS errors; captured desktop and mobile previews')
if __name__=='__main__':run()
