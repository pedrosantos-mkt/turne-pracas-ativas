import requests, json, os, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pracas import GURU_TOKEN
T=GURU_TOKEN()
H={'Authorization':'Bearer '+T,'Accept':'application/json','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'}
def slice_(a,b):
  out=[];cur=None
  while True:
    p={'ordered_at_ini':a,'ordered_at_end':b}
    if cur: p['cursor']=cur
    for t in range(5):
      try: r=requests.get('https://digitalmanager.guru/api/v2/transactions',headers=H,params=p,timeout=(10,60)); break
      except Exception as e: print(e)
    if r.status_code!=200: print(a,r.status_code,r.text[:200]); return out
    j=r.json(); out+=j.get('data',[])
    if not j.get('has_more_pages'): return out
    cur=j.get('next_cursor')
E=dt.date.today(); s=E-dt.timedelta(days=150); sl=[]
while s<=E:
  e=min(s+dt.timedelta(days=4),E); sl.append((str(s),str(e))); s=e+dt.timedelta(days=1)
with ThreadPoolExecutor(8) as ex: rs=list(ex.map(lambda x:slice_(*x),sl))
allt=[t for r in rs for t in r]
json.dump(allt,open('raw/guru.json','w'))
print(len(allt))
