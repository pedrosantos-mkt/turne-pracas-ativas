# CPM, CTR e CPC do Gerenciador por grupo de público (quente, frio, mix) em cada praça
import requests, json, time, collections
from pracas import META_TOKEN, tag_of
T=META_TOKEN(); ACT='act_171474008015977'
ins=json.load(open('raw/ins.json')); adsets=json.load(open('raw/adsets.json'))
F='spend,impressions,cpm,ctr,inline_link_click_ctr,cost_per_inline_link_click'
grupos=collections.defaultdict(list)
for cid,rows in adsets.items():
  for r in rows: grupos[(ins[cid]['city'],tag_of(r['adset_name'],ins[cid]['name']))].append(r['adset_id'])
def get(ids):
  p={'level':'account','date_preset':'maximum','fields':F,'access_token':T,
     'filtering':json.dumps([{'field':'adset.id','operator':'IN','value':ids}])}
  for a in range(5):
    r=requests.get(f'https://graph.facebook.com/v21.0/{ACT}/insights',params=p,timeout=120).json()
    if 'error' not in r: return (r.get('data') or [{}])[0]
    print(r['error'].get('message')); time.sleep(15*(a+1))
  return {}
res={}
for (city,tag),ids in grupos.items():
  res.setdefault(city,{})[tag]=get(ids)
json.dump(res,open('raw/metricas_publico.json','w'))
for city,v in res.items(): print(city,{t:(x.get('cpm'),x.get('inline_link_click_ctr')) for t,x in v.items()})
