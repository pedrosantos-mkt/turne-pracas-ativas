from pracas import seguro
import requests, json, os, re, time
from pracas import pracas, todas_pracas, META_TOKEN
import glob
T=META_TOKEN()
d=json.load(open('raw/allmv.json'))
EM_CACHE={os.path.basename(f)[:-5] for f in glob.glob('cache/pracas/*.json')}
json.dump(todas_pracas(d),open('raw/pracas_todas.json','w'),ensure_ascii=False)
P=pracas(d,em_cache=EM_CACHE)
print(len(P),'praças a coletar,',len(EM_CACHE),'no cache')
json.dump(P,open('raw/pracas.json','w'),ensure_ascii=False)
nm={c['id']:c for c in d}
sel={cid:(code,nm[cid]) for code,p in P.items() for cid in p['campanhas']}
print(len(sel))
F='campaign_id,spend,impressions,inline_link_clicks,actions,action_values'
def get(cid,extra):
  for a in range(6):
    try:
      r=requests.get(f'https://graph.facebook.com/v21.0/{cid}/insights',params={'access_token':T,'fields':F,'date_preset':'maximum','limit':500,**extra},timeout=90).json()
      if 'error' in r:
        print(cid,r['error'].get('message')); time.sleep(30*(a+1)); continue
      return r['data']
    except Exception as e: print(seguro(e)); time.sleep(10)
res={}
for cid,(ci,c) in sel.items():
  res[cid]={'city':ci,'name':c['name'],'status':c['effective_status'],'start':c['start_time'],
            'total':get(cid,{}),'daily':get(cid,{'time_increment':1})}
json.dump(res,open('raw/ins.json','w'))
print('ok')
