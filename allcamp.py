import requests, json, os
from pracas import META_TOKEN
T=META_TOKEN()
import datetime as dt
LIMITE='2025-09-01'   # campanhas das praças do ano (eventos desde 01/01/2026)
out=[];url='https://graph.facebook.com/v21.0/act_171474008015977/campaigns'
p={'access_token':T,'fields':'id,name,effective_status,start_time,stop_time','limit':500}
import time
while url:
    for a in range(8):   # limite de chamadas do Meta: espera e tenta de novo (até ~12 min)
        r=requests.get(url,params=p,timeout=90).json()
        if 'error' not in r: break
        print(r['error'].get('message')); time.sleep(30*(a+1))
    else: raise SystemExit('Meta recusou a lista de campanhas; nada é publicado nesta rodada')
    out+=r['data']; url=r.get('paging',{}).get('next'); p=None
    if out and out[-1].get('start_time','')<LIMITE: break
if not out: raise SystemExit('0 campanhas no Meta; nada é publicado nesta rodada')
json.dump(out,open('raw/allmv.json','w'))
print(len(out))
