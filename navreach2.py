import re, sys, importlib.util
spec=importlib.util.spec_from_file_location('views','/home/claude/w247/views.py'); V=importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
enc=sys.argv[1]; dec=sys.argv[2]
allv=V.views(enc)[0]
s=open(dec,encoding='utf-8').read()
i=s.index('const titleMap'); j=s.index('\n    };', i); rest=s[:i]+s[j:]
routes={}
for v in allv:
    strong=len(re.findall(r"go\('"+v+r"'\)|view: '"+v+r"'|\['"+v+r"', '|_open\w*\('"+v+r"'\)", rest))
    quoted=len(re.findall(r"'"+v+r"'", rest))
    routes[v]=(strong,quoted)
none=[v for v in allv if routes[v][1]==0]
print(enc, '| screens', len(allv), '| no route of any kind', len(none), none[:20], '| direct route', sum(1 for v in allv if routes[v][0]>0), '| array-built route only', sum(1 for v in allv if routes[v][0]==0 and routes[v][1]>0))
