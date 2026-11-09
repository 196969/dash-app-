"""item420_roster.py <index.html> <out.json> — derives the Founders 72 roster and weight from the app's own _councilRoster(), never typed."""
import asyncio,json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from pxconst import FIND
from playwright.async_api import async_playwright
async def main(h):
    async with async_playwright() as p:
        b=await p.chromium.launch(); c=await b.new_context(); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg=await c.new_page(); await pg.goto('file://'+os.path.abspath(h),timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND)
        r=await pg.evaluate("()=>{const d=window.__dash; const R=d._councilRoster(); const L=[{seat:1,name:R.chair.name,weight:R.chair.weight,ground:'chair'}].concat(R.governing.map((g,i)=>({seat:2+i,name:g.name,weight:g.weight,ground:g.ground})), R.adv.map((a,i)=>({seat:6+i,name:a.name,weight:a.weight,ground:a.key+' · '+a.tier}))); return {L, seats:R.seats, totalW:R.totalW}}")
        await b.close(); return r
R=asyncio.run(main(sys.argv[1])); json.dump(R,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
r=R['L']; print('seats',R['seats'],'totalW',R['totalW'],'sum',sum(x['weight'] for x in r)); [print(x['seat'],x['name'],x['weight'],x['ground']) for x in r]
