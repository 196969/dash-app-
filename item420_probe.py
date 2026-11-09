"""item420_probe.py <index.html> <script.js> — loads the app headless (tour dismissed, storage cleared) and runs one page-side script, printing its JSON result and any page errors."""
import asyncio,json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from pxconst import FIND
from playwright.async_api import async_playwright
async def main(h,js):
    async with async_playwright() as p:
        b=await p.chromium.launch(); c=await b.new_context(viewport={'width':1440,'height':900}); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg=await c.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)[:200]))
        await pg.goto('file://'+os.path.abspath(h),timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND)
        r=await pg.evaluate(js); await b.close(); return r,errs
r,e=asyncio.run(main(sys.argv[1],open(sys.argv[2]).read()))
print(json.dumps(r,ensure_ascii=False,indent=1)[:int(os.environ.get('LIM','12000'))]); print('pageErrors',e)
