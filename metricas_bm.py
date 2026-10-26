# CPM e CTR como o Gerenciador de Anúncios calcula, por praça (total e por dia), somando as campanhas da praça
import requests, json, time
from pracas import META_TOKEN
T=META_TOKEN(); ACT='act_171474008015977'
P=json.load(open('raw/pracas.json'))
F='spend,impressions,cpm,ctr,inline_link_click_ctr,inline_link_clicks,cost_per_inline_link_click'
def get(p):
  out=[]; url=f'https://graph.facebook.com/v21.0/{ACT}/insights'; p={**p,'access_token':T}
  while url:
    for a in range(5):
      r=requests.get(url,params=p,timeout=120).json()
      if 'error' not in r: break
      print(r['error'].get('message')); time.sleep(15*(a+1))
    out+=r.get('data',[]); url=r.get('paging',{}).get('next'); p=None
  return out
res={}
for code,p in P.items():
  filtro=json.dumps([{'field':'campaign.id','operator':'IN','value':p['campanhas']}])
  tot=get({'level':'account','date_preset':'maximum','fields':F,'filtering':filtro})
  dia=get({'level':'account','date_preset':'maximum','time_increment':1,'limit':500,'fields':F,'filtering':filtro})
  res[code]={'total':tot[0] if tot else {},'dia':{r['date_start']:r for r in dia}}
json.dump(res,open('raw/metricas_bm.json','w'))
for code,v in res.items(): t=v['total']; print(code,t.get('cpm'),t.get('inline_link_click_ctr'),t.get('ctr'),len(v['dia']))
