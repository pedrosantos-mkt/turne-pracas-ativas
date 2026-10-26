# Envios dos formulários da turnê (página, UTMs, e-mail) desde 15/08
import json,requests,os
from concurrent.futures import ThreadPoolExecutor
from pracas import HUBSPOT_TOKEN
T=HUBSPOT_TOKEN()
import datetime as dt
desde=(dt.date.today()-dt.timedelta(days=150)).isoformat()
forms=[];after=None
while True:
  p={'limit':100}
  if after: p['after']=after
  r=requests.get('https://api.hubapi.com/marketing/v3/forms',headers={'Authorization':'Bearer '+T},params=p,timeout=60).json()
  forms+=r.get('results',[]); after=r.get('paging',{}).get('next',{}).get('after')
  if not after: break
forms=[f for f in forms if 'TURNEMAQUINADEVENDAS' in f['name'].upper() and f.get('createdAt','')>=desde]
def pull(f):
  out=[];after=None
  while True:
    p={'limit':50}
    if after: p['after']=after
    for t in range(4):
      try: r=requests.get(f"https://api.hubapi.com/form-integrations/v1/submissions/forms/{f['id']}",headers={'Authorization':'Bearer '+T},params=p,timeout=60).json(); break
      except Exception as e: r={}
    for s in r.get('results',[]):
      v={x['name']:x['value'] for x in s.get('values',[])}
      out.append({'form':f['name'],'at':s.get('submittedAt'),'page':s.get('pageUrl'),**{k:v.get(k) for k in ['email','utm_campaign','utm_term','utm_content','utm_source','annualrevenue']}})
    after=r.get('paging',{}).get('next',{}).get('after')
    if not after: return out
with ThreadPoolExecutor(6) as ex: rs=list(ex.map(pull,forms))
subs=[s for r in rs for s in r]
json.dump(subs,open('raw/hs_subs.json','w'),ensure_ascii=False)
print(len(forms),len(subs))
