import re, json, subprocess, sys, os, warnings
warnings.filterwarnings("ignore")
src=open(sys.argv[1],encoding='utf-8').read(); tag=sys.argv[2]
# 1 · node/acorn: the app's logic script parses as JavaScript
m=re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', src, re.S); js=m.group(1)
open(f'/tmp/logic_{tag}.js','w',encoding='utf-8').write(js)
root=subprocess.run(['npm','root','-g'],capture_output=True,text=True).stdout.strip()
r=subprocess.run(['node','-e',"const a=require(process.argv[2]+'/acorn');const s=require('fs').readFileSync(process.argv[1],'utf8');try{a.parse(s,{ecmaVersion:'latest',sourceType:'script'});console.log('PARSE OK',s.length,'chars')}catch(e){console.log('PARSE FAIL',e.message)}", f'/tmp/logic_{tag}.js', root],capture_output=True,text=True); print('1 acorn:', (r.stdout+r.stderr).strip()[:200])
# 2 · sc-if balance: every <sc-if> and <sc-for> closes, in order, with no stray closer
tpl=src[:m.start()]
for t in ['sc-if','sc-for']:
    depth=0; neg=0; mx=0
    for x in re.finditer(r'<'+t+r'\b|</'+t+'>', tpl):
        depth += 1 if not x.group(0).startswith('</') else -1; mx=max(mx,depth)
        if depth<0: neg+=1
    print(f'2 {t} balance: open {len(re.findall("<"+t+r"\b",tpl))} close {tpl.count("</"+t+">")} final depth {depth} stray closers {neg} max nesting {mx}')
# 4 · one-word sentences in user-facing strings: a sentence of a single word ending in . ! or ?
strs=re.findall(r"'((?:[^'\\]|\\.){12,})'", js)
hits=set()
for s0 in strs:
    s1=s0.encode().decode('unicode_escape', errors='ignore') if chr(92)+'u' in s0 else s0
    for sent in re.split(r'(?<=[.!?])\s+', s1):
        w=sent.strip()
        if re.fullmatch(r"[A-Z][a-z’']+[.!?]", w) and w not in ('Opened.','Done.'): hits.add(w)
print('4 one-word sentences:', len(hits), sorted(hits)[:30])
