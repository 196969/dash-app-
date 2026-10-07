"""brandmark.py <index.html> — the brand marker, by render path.
Retired in Pass 15: the 'wordmark 1' substring marker, which only ever matched a comment in the PowerPoint exporter.
This asserts the theme view model's brand name is rendered as visible text on the Today screen. Exit 1 if it is not."""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from pxconst import CHROME, FIND
from playwright.async_api import async_playwright
async def main(path):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME); ctx = await b.new_context(); await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}"); pg = await ctx.new_page()
        await pg.goto('file://'+os.path.abspath(path), timeout=120000); await pg.wait_for_timeout(4500); assert await pg.evaluate(FIND)
        r = await pg.evaluate("()=>{ const name=window.__dash.renderVals().themeVM.brandName; const els=[...document.querySelectorAll('body *')].filter(e=>e.childElementCount===0 && e.textContent.trim()===name && e.getClientRects().length); return {name, rendered: els.length, where: els.slice(0,2).map(e=>e.tagName.toLowerCase()+(e.className?'.'+String(e.className).split(' ')[0]:''))}; }")
        await b.close(); return r
r = asyncio.run(main(sys.argv[1])); ok = r['rendered'] > 0
print(('BRAND MARK OK' if ok else 'BRAND MARK MISSING') + f": '{r['name']}' rendered as visible text in {r['rendered']} element(s) {r['where']}")
sys.exit(0 if ok else 1)
