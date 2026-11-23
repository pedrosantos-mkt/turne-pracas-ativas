from pracas import seguro
import requests, json, os, time, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pracas import GURU_TOKEN
T=GURU_TOKEN()
H={'Authorization':'Bearer '+T,'Accept':'application/json','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'}
def slice_(a,b):
  out=[];cur=None
  while True:
    p={'ordered_at_ini':a,'ordered_at_end':b}
    if cur: p['cursor']=cur
    r=None
    for t in range(10):
      try:
        r=requests.get('https://digitalmanager.guru/api/v2/transactions',headers=H,params=p,timeout=(10,60))
        if r.status_code==429 or r.status_code>=500: time.sleep(min(120,10*(t+1))); continue
        break
      except Exception as e: print(seguro(e)); time.sleep(5)
    # sem resposta completa a coleta para (melhor não publicar do que publicar vendas faltando)
    if r is None or r.status_code!=200: raise SystemExit(f'Guru falhou em {a}: {r.status_code if r is not None else "sem resposta"}')
    j=r.json(); out+=j.get('data',[])
    if not j.get('has_more_pages'): return out
    cur=j.get('next_cursor')
E=dt.date.today(); s=dt.date(2025,9,1); sl=[]   # vendas das praças do ano
while s<=E:
  e=min(s+dt.timedelta(days=4),E); sl.append((str(s),str(e))); s=e+dt.timedelta(days=1)
with ThreadPoolExecutor(3) as ex: rs=list(ex.map(lambda x:slice_(*x),sl))
allt=[t for r in rs for t in r]
json.dump(allt,open('raw/guru.json','w'))
print(len(allt))
