# URL de destino e insights por anúncio, para o quadro de páginas
import requests, json, os, time
from pracas import META_TOKEN
T=META_TOKEN()
ins=json.load(open('raw/ins.json'))
def get(url,p):
  out=[]
  while url:
    for a in range(6):
      try:
        r=requests.get(url,params=p,timeout=90).json()
        if 'error' in r: print(r['error'].get('message')); time.sleep(30*(a+1)); continue
        break
      except Exception as e: print(e); time.sleep(10)
    out+=r.get('data',[]); url=r.get('paging',{}).get('next'); p=None
  return out
res={}
for cid in ins:
  ads=get(f'https://graph.facebook.com/v21.0/{cid}/ads',{'access_token':T,'limit':200,'fields':'id,name,adset_id,creative{asset_feed_spec{link_urls},object_story_spec{link_data{link},video_data{call_to_action}}}'})
  st=get(f'https://graph.facebook.com/v21.0/{cid}/insights',{'access_token':T,'level':'ad','date_preset':'maximum','limit':500,'fields':'ad_id,spend,impressions,inline_link_clicks,actions'})
  res[cid]={'ads':ads,'ins':st}
json.dump(res,open('raw/ads.json','w'))
print(sum(len(v['ads']) for v in res.values()), sum(len(v['ins']) for v in res.values()))
