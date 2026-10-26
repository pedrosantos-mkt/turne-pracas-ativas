import json,requests,os,collections,unicodedata
g=json.load(open('raw/guru.json'))
N=lambda s:unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().upper().replace(' ','')
from pracas import guru_da_praca
PR=json.load(open('raw/pracas.json')).values()
from pracas import HUBSPOT_TOKEN
T=HUBSPOT_TOKEN()
emails=sorted({(x['contact'].get('email') or '').lower().strip() for x in g if x['status']=='approved' and (x['payment']['total'] or 0)>0 and any(guru_da_praca(x['product']['name'],p) for p in PR)}-{''})
print(len(emails))
P=['email','annualrevenue','qual_o_seu_cargo_','ti__cargo','ti__form____cargo','jobtitle']
res={}
for i in range(0,len(emails),100):
  r=requests.post('https://api.hubapi.com/crm/v3/objects/contacts/batch/read',headers={'Authorization':'Bearer '+T},json={'idProperty':'email','properties':P,'inputs':[{'id':e} for e in emails[i:i+100]]},timeout=60)
  for c in r.json().get('results',[]): res[c['properties']['email'].lower()]=c['properties']
json.dump(res,open('raw/hs.json','w'))
print(len(res))
for p in P[2:]: print(p, collections.Counter(v.get(p) for v in res.values()).most_common(8))
