# Rebuilds founders-true.html from founders-true-figures.json. Run gen_ft_figures.py first.
import sys,json,re; sys.path.insert(0,'/home/claude'); from codec import *
page,figs,out=sys.argv[1],sys.argv[2],sys.argv[3]
F=json.load(open(figs)); s=open(page,encoding='utf-8').read(); a,m,c=split(s); src=dec(m)
old=re.search(r"static DEFAULTS = \{[^}]*\};",src).group(0)
missing=[k for k,v in F.items() if v['value'] is None]
if missing: sys.exit('not derivable, refusing to carry old values: '+', '.join(missing))
def js(v): return "'"+v+"'" if isinstance(v,str) else (('%.2f'%v).rstrip('0').rstrip('.') if isinstance(v,float) else str(v))
order=['asOf','revenue','expenses','cash','burn','pipeline','clients','largest','recurring','tb','nextDeal','rate']
new="static DEFAULTS = { "+', '.join(k+': '+js(F[k]['value']) for k in order)+" };"
src=src.replace(old,new,1)
src=re.sub(r"static KEY = 'dashrite-founders-ten-lenses-truedata-[^']*';","static KEY = 'dashrite-founders-ten-lenses-truedata-"+re.sub(r'\W','',F['asOf']['value']).lower()+"';",src,count=1)
open(out,'wb').write(build(a,src,c)); print('old:',old); print('new:',new)
