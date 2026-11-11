# Junta data.json + logo no template e gera index.html (Artifact) e site/index.html (Vercel)
import json,base64,datetime as dt,os
d=json.load(open('data.json')); d['hoje']=dt.date.today().isoformat()
# trava: nunca publicar painel vazio ou menor que as praças já encerradas guardadas (ex.: Meta limitou as chamadas)
import glob
guardadas=len(glob.glob('cache/pracas/*.json'))
if not d['cidades'] or len(d['cidades'])<guardadas: raise SystemExit(f"painel com {len(d['cidades'])} praças (guardadas: {guardadas}); nada é publicado")
logo='data:image/webp;base64,'+base64.b64encode(open('logo.webp','rb').read()).decode()
t=open('template.html').read().replace('__LOGO__',logo).replace('__DATA__',json.dumps(d,ensure_ascii=False))
open('index.html','w').write(t)
os.makedirs('site',exist_ok=True)
open('site/index.html','w').write('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'+t.replace('<div class="wrap">','</head><body><div class="wrap">',1)+'</body></html>')
print(len(t))
