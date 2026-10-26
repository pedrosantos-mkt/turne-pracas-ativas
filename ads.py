# URL de destino e insights por anúncio (consulta única na conta, filtrada pelas campanhas das praças)
import requests, json, time, collections
from pracas import META_TOKEN
T=META_TOKEN(); ACT='act_171474008015977'
ins=json.load(open('raw/ins.json')); ids=list(ins)
def get(path,p,base=None,tentativas=3):
  """Pagina uma consulta; devolve None se o Meta recusar depois das tentativas."""
  out=[]; url=f'https://graph.facebook.com/v21.0/{base or ACT}/{path}'; p={**p,'access_token':T}
  while url:
    for a in range(tentativas):
      try:
        r=requests.get(url,params=p,timeout=120).json()
        if 'error' not in r: break
        print(r['error'].get('message')); time.sleep(10*(a+1))
      except Exception as e: print(e); time.sleep(10); r={'error':str(e)}
    if 'error' in r: return None
    out+=r.get('data',[]); url=r.get('paging',{}).get('next'); p=None
  return out
filtro=lambda ch: json.dumps([{'field':'campaign.id','operator':'IN','value':ch}])
ads=[];st=[]
CAMPOS_AD='id,name,adset_id,campaign_id,creative{asset_feed_spec{link_urls},object_story_spec{link_data{link},video_data{call_to_action}}}'
CAMPOS_INS='ad_id,campaign_id,spend,impressions,inline_link_clicks,actions'
for i in range(0,len(ids),15):
  ch=ids[i:i+15]
  a=get('ads',{'limit':300,'filtering':filtro(ch),'fields':CAMPOS_AD})
  s_=get('insights',{'level':'ad','date_preset':'maximum','limit':500,'filtering':filtro(ch),'fields':CAMPOS_INS})
  if a is None or s_ is None:
    # o Meta recusou o lote: busca campanha a campanha
    print('lote recusado, buscando campanha a campanha')
    a=[];s_=[]
    for cid in ch:
      a+=get('ads',{'limit':200,'fields':CAMPOS_AD},base=cid,tentativas=5) or []
      s_+=get('insights',{'level':'ad','date_preset':'maximum','limit':500,'fields':CAMPOS_INS},base=cid,tentativas=5) or []
  ads+=a; st+=s_
res={cid:{'ads':[],'ins':[]} for cid in ids}
for a in ads: res.setdefault(a['campaign_id'],{'ads':[],'ins':[]})['ads'].append(a)
for r in st: res.setdefault(r['campaign_id'],{'ads':[],'ins':[]})['ins'].append(r)
# conferência: gasto por anúncio tem que bater com o gasto das campanhas
gasto_ads=sum(float(r['spend']) for r in st)
gasto_camp=sum(float(x['spend']) for v in ins.values() for x in (v['total'] or []))
print(len(ads),'anúncios',len(st),'linhas', round(gasto_ads),'x',round(gasto_camp))
if abs(gasto_ads-gasto_camp)>max(50,gasto_camp*0.01): raise SystemExit('gasto por anúncio não bate com o das campanhas')
json.dump(res,open('raw/ads.json','w'))
