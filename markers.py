#!/usr/bin/env python3
"""The eight survival markers (Build Brief, 7 Oct 2026), counted in the decoded source. Usage: python3 markers.py <index.html> [--expect <json>]
Counts are literal occurrences in the decoded Dash source; the brief's 7 Oct figures are shown beside each, and a moved figure is reported, never re-baselined.
Exit 1 if any presence marker is absent, or if --expect is given and any count differs from it."""
import json,re,subprocess,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(sys.argv[1])) or '.')
from codec import decode
s=decode(open(sys.argv[1],encoding='utf-8').read())[1]
inv=lambda n: bool(re.search(r"id: '?"+n+r"'?[^}]{0,400}status: 'Paid'",s)) or bool(re.search(r"status: 'Paid'[^}]{0,400}id: '?"+n+r"'?",s))
M={'1 invoices 1004 and 1005 Paid':inv('1004') and inv('1005'),
 '2 portalhome':s.count('portalhome'),'3 webleads':s.count('webleads'),'4 fndxcoverage':s.count('fndxcoverage'),'5 _lensBoardKeys':s.count('_lensBoardKeys'),
 '6 Bella with rawSpeak and the female-only guard':('Bella' in s) and ('rawSpeak' in s) and bool(re.search(r'female',s,re.I)),
 '7 screen ids dashiq, memory, autopilot, cmdxmindset':all(re.search(r"\b"+v+r": \[",s) for v in ('dashiq','memory','autopilot','cmdxmindset')),
 '8 brandmark.py':None}
d=os.path.dirname(os.path.abspath(sys.argv[1])); b=subprocess.run(['python3',os.path.join(d,'brandmark.py'),sys.argv[1]],capture_output=True,text=True); M['8 brandmark.py']=b.returncode==0
BRIEF={'2 portalhome':1,'3 webleads':22,'4 fndxcoverage':10,'5 _lensBoardKeys':15}
for k,v in M.items(): print(f'{k}: {v}'+(f'  (Build Brief 7 Oct: {BRIEF[k]})' if k in BRIEF else ''))
bad=[k for k,v in M.items() if v is False or v==0]
if '--expect' in sys.argv:
    E=json.loads(open(sys.argv[sys.argv.index('--expect')+1]).read()); bad+=[f'{k} moved {E[k]} -> {M[k]}' for k in E if E[k]!=M[k]]
json.dump(M,open('/tmp/markers-last.json','w')); print('MARKERS', 'HELD 8 of 8' if not bad else 'REFUSED: '+'; '.join(map(str,bad))); sys.exit(1 if bad else 0)
