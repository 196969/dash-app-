import re, sys, importlib.util
import os
spec=importlib.util.spec_from_file_location('views', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views.py')); V=importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
# Usage: navreach2.py <index.html> [decoded.html]. The build is decoded here with codec.py, so the
# screens and the references always come from the same build. A second file is optional and is
# refused unless it is exactly that build's decoded source. Exits 1 on any orphaned screen.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from codec import decode as _decode
enc=sys.argv[1]
allv=V.views(enc)[0]
s=_decode(open(enc,encoding='utf-8').read())[1]
if len(sys.argv) > 2 and open(sys.argv[2],encoding='utf-8').read() != s:
    print('REFUSED: ' + sys.argv[2] + ' is not the decoded source of ' + enc + '; screens and references would come from different builds'); sys.exit(1)
i=s.index('const titleMap'); j=s.index('\n    };', i); rest=s[:i]+s[j:]
routes={}
for v in allv:
    strong=len(re.findall(r"go\('"+v+r"'\)|view: '"+v+r"'|\['"+v+r"', '|_open\w*\('"+v+r"'\)", rest))
    quoted=len(re.findall(r"'"+v+r"'", rest))
    routes[v]=(strong,quoted)
none=[v for v in allv if routes[v][1]==0]
print(enc, '| screens', len(allv), '| no route of any kind', len(none), none[:20], '| direct route', sum(1 for v in allv if routes[v][0]>0), '| array-built route only', sum(1 for v in allv if routes[v][0]==0 and routes[v][1]>0))
if none: sys.exit(1)
