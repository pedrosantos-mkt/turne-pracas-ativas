from pracas import seguro
# Miniatura dos criativos que podem entrar no ranking (busca por lotes de IDs, depois do quadros.py)
import json, requests, time
from pracas import META_TOKEN
T=META_TOKEN()
d=json.load(open('data.json'))
alvo=[r for c in d['cidades'] for r in c['criativos'] if r.get('ad') and r.get('spend',0)>=150]
ids=sorted({r['ad'] for r in alvo}); thumb={}
for i in range(0,len(ids),40):
  for a in range(4):
    try:
      r=requests.get('https://graph.facebook.com/v21.0/',params={'access_token':T,'ids':','.join(ids[i:i+40]),'fields':'creative{thumbnail_url}'},timeout=90).json()
      if 'error' in r: print(r['error'].get('message')); time.sleep(15*(a+1)); continue
      for k,v in r.items(): thumb[k]=(v.get('creative') or {}).get('thumbnail_url')
      break
    except Exception as e: print(seguro(e)); time.sleep(10)
for r in alvo: r['thumb']=thumb.get(r['ad'])
json.dump(d,open('data.json','w'),ensure_ascii=False)
print(len(ids),'criativos,',sum(1 for v in thumb.values() if v),'miniaturas')
