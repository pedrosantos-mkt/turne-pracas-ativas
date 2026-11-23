from pracas import seguro
# Insights por conjunto (adset) das campanhas de compra de cada praça
import requests, json, os, time
from pracas import META_TOKEN
T=META_TOKEN()
ins=json.load(open('raw/ins.json'))
F='adset_id,adset_name,campaign_id,spend,impressions,inline_link_clicks,actions'
out={}
for cid,v in ins.items():
  for a in range(6):
    try:
      r=requests.get(f'https://graph.facebook.com/v21.0/{cid}/insights',params={'access_token':T,'fields':F,'level':'adset','date_preset':'maximum','limit':500},timeout=90).json()
      if 'error' in r: print(cid,r['error'].get('message')); time.sleep(30*(a+1)); continue
      out[cid]=r['data']; break
    except Exception as e: print(seguro(e)); time.sleep(10)
json.dump(out,open('raw/adsets.json','w'))
print(sum(len(x) for x in out.values()))
