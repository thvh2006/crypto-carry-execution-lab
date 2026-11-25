"""Execute evidence notebooks from clean namespaces, retaining tables and SVGs."""
import contextlib,html,io,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);sys.path.insert(0,str(ROOT))
books=json.loads((ROOT/'scripts/market_notebook_cells.json').read_text());destination=ROOT/'notebooks';destination.mkdir(exist_ok=True)
setup="""from pathlib import Path
import os,sys,html
root=Path.cwd()
if not (root/'carry').exists():root=root.parent
os.chdir(root)
sys.path.insert(0,str(root))
def show_svg(svg):
    if '_emit_data' in globals():_emit_data({'image/svg+xml':svg})
    else:
        from IPython.display import display,SVG
        display(SVG(svg))
def show_table(headers,rows):
    markup='<table><thead><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'
    if '_emit_data' in globals():_emit_data({'text/html':markup})
    else:
        from IPython.display import display,HTML
        display(HTML(markup))
"""
for slug,title,authored in books:
 start=time.perf_counter();cells=[{'cell_type':'markdown','metadata':{},'source':['# '+title+'\n','Frozen study eed008040d6c6d18. Post-study evidence review, hypothetical fills.\n']}]
 namespace={};count=0
 for cell in [{'cell_type':'code','source':setup}]+authored:
  source=cell['source']
  if cell['cell_type']=='markdown':cells.append({'cell_type':'markdown','metadata':{},'source':source.splitlines(keepends=True)});continue
  count+=1;outputs=[];stdout,stderr=io.StringIO(),io.StringIO();namespace['_emit_data']=lambda data:outputs.append({'output_type':'display_data','data':data,'metadata':{}})
  t=time.perf_counter()
  with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):exec(compile(source,slug,'exec'),namespace)
  for name,stream in [('stdout',stdout),('stderr',stderr)]:
   if stream.getvalue():outputs.append({'output_type':'stream','name':name,'text':stream.getvalue().splitlines(keepends=True)})
  cells.append({'cell_type':'code','execution_count':count,'metadata':{'execution_seconds':round(time.perf_counter()-t,6)},'source':source.splitlines(keepends=True),'outputs':outputs})
 nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]},'evidence':{'source_run':'eed008040d6c6d18','executed_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':round(time.perf_counter()-start,6),'scope':'Post-study explanation; no new holdout or tuning'}},'nbformat':4,'nbformat_minor':4}
 (destination/(slug+'.ipynb')).write_text(json.dumps(nb,indent=2))
 print(slug,'cells',len(cells),'rich outputs',sum(o['output_type']=='display_data' for c in cells for o in c.get('outputs',[])))
