"""Known-answer controls for battery.py. Each plants a fault the instrument must report, on the same build it will measure, and fails loudly if the instrument misses it."""
import asyncio,json,os,re,sys,tempfile,shutil,subprocess
import battery as B
def plant(html,old,new,out):
    raw=open(html,encoding='utf-8').read(); pre,src,post=B.decode(raw); assert src.count(old)>=1,('anchor missing',old[:40])
    open(out,'w',encoding='utf-8').write(B.encode(pre,src.replace(old,new,1),post))
def shell(html,extra,out):
    raw=open(html,encoding='utf-8').read(); i=raw.rfind('</body>'); assert i>0; open(out,'w',encoding='utf-8').write(raw[:i]+extra+raw[i:])
def run(name,args):
    html=args[0]; d=tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(html))); ok=False
    try:
        if name in ('textdiff','compare'):
            os.environ['BATTERY_VIEWS']='cncl,safety,fndxgoldratt'
            alt=os.path.join(d,'alt.html'); plant(html,'lens intelligence</div>','lens intelligenze</div>',alt)
            a,b=os.path.join(d,'a.json'),os.path.join(d,'b.json'); asyncio.run(B.textdiff(html,1440,a)); asyncio.run(B.textdiff(alt,1440,b))
            D=B.compare(a,b); ok=D is not None and 'fndxgoldratt' in D and 'cncl' not in D
            R=json.load(open(b)); R['texts']['cncl']='ERR Target crashed'; json.dump(R,open(b,'w')); ok=ok and B.compare(a,b) is None
        elif name in ('census','tbr'):
            book=args[1]; J=json.load(open(book)); st=J.get('state',J); acct=next(x for x in st['coa'] if re.match('asset',str(x.get('type')),re.I)); acct['balance']=float(acct['balance'])+100
            bad=os.path.join(d,'book.json'); json.dump(J,open(bad,'w'))
            a,b=asyncio.run(B.tbr(html,html,book)); c,_=asyncio.run(B.tbr(html,html,bad))
            ok=a['dr']==a['cr']==4382.19 and c['dr']!=c['cr']
        elif name=='render':
            alt=os.path.join(d,'alt.html'); shell(html,'<script>setInterval(function(){var m=[].slice.call(document.querySelectorAll("div.m-scroll")).pop(); if(m&&!m.querySelector("#probe")){var p=document.createElement("div"); p.id="probe"; p.style.cssText="width:4000px;height:4px"; m.appendChild(p); p.animate([{transform:"translateX(0)"},{transform:"translateX(10px)"}],{duration:1000,iterations:Infinity});}},150); setTimeout(function(){throw new Error("probe")},50)</script>',alt)
            o=asyncio.run(B.render(alt,['cncl'])); w=o[1440]; ok=w['page errors']>=1 and w['sideways']==['cncl'] and max(w['reduced motion (400/1500/4000 ms)']['cncl'])>=1
        elif name=='topbar':
            os.environ['BATTERY_VIEWS']='cncl,safety'; alt=os.path.join(d,'alt.html'); shell(html,'<script>setInterval(function(){ if(!document.getElementById("probeCss")){ var st=document.createElement("style"); st.id="probeCss"; st.textContent="header button[aria-label*=Second]{display:none!important}"; document.head.appendChild(st); } },100)</script>',alt)
            r1=asyncio.run(B.topbar(html,os.path.join(d,'t1.json'))); r2=asyncio.run(B.topbar(alt,os.path.join(d,'t2.json')))
            ok=all(c==1 for c in r1.values()) and all(c==0 for c in r2.values())
        elif name=='iso':
            r=asyncio.run(B.iso(html,html)); ok=r['base1'][1]==r['new'][1] and bool(r['base1'][0])
    finally: shutil.rmtree(d,ignore_errors=True)
    print('CONTROL',name,'PASSED — the instrument reported the planted fault' if ok else 'FAILED — the instrument missed the planted fault; its results are not evidence'); sys.exit(0 if ok else 1)
