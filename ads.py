# URL de destino e insights por anúncio (consulta única na conta, filtrada pelas campanhas das praças)
import requests, json, time, collections
from pracas import META_TOKEN
T=META_TOKEN(); ACT='act_171474008015977'
ins=json.load(open('raw/ins.json')); ids=list(ins)
def get(path,p):
  out=[]; url=f'https://graph.facebook.com/v21.0/{ACT}/{path}'; p={**p,'access_token':T}
  while url:
    for a in range(6):
      try:
        r=requests.get(url,params=p,timeout=120).json()
        if 'error' in r: print(r['error'].get('message')); time.sleep(20*(a+1)); continue
        break
      except Exception as e: print(e); time.sleep(10)
    out+=r.get('data',[]); url=r.get('paging',{}).get('next'); p=None
  return out
filtro=lambda ch: json.dumps([{'field':'campaign.id','operator':'IN','value':ch}])
ads=[];st=[]
for i in range(0,len(ids),50):
  ch=ids[i:i+50]
  ads+=get('ads',{'limit':300,'filtering':filtro(ch),'fields':'id,name,adset_id,campaign_id,creative{asset_feed_spec{link_urls},object_story_spec{link_data{link},video_data{call_to_action}}}'})
  st+=get('insights',{'level':'ad','date_preset':'maximum','limit':500,'filtering':filtro(ch),'fields':'ad_id,campaign_id,spend,impressions,inline_link_clicks,actions'})
res={cid:{'ads':[],'ins':[]} for cid in ids}
for a in ads: res.setdefault(a['campaign_id'],{'ads':[],'ins':[]})['ads'].append(a)
for r in st: res.setdefault(r['campaign_id'],{'ads':[],'ins':[]})['ins'].append(r)
# conferência: gasto por anúncio tem que bater com o gasto das campanhas
gasto_ads=sum(float(r['spend']) for r in st)
gasto_camp=sum(float(x['spend']) for v in ins.values() for x in (v['total'] or []))
print(len(ads),'anúncios',len(st),'linhas', round(gasto_ads),'x',round(gasto_camp))
if abs(gasto_ads-gasto_camp)>max(50,gasto_camp*0.01): raise SystemExit('gasto por anúncio não bate com o das campanhas')
json.dump(res,open('raw/ads.json','w'))
