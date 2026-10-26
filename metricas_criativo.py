# CTR e CPM do Gerenciador por criativo do ranking (soma dos anúncios com o mesmo nome), em lotes de 50 pedidos
import requests, json, time
from pracas import META_TOKEN
T=META_TOKEN(); ACT='act_171474008015977'
d=json.load(open('data.json'))
alvo=[r for c in d['cidades'] for r in c['criativos'] if r.get('ads') and r.get('spend',0)>=150]
F='cpm,ctr,inline_link_click_ctr,cost_per_inline_link_click'
f_=lambda x,k,dv=1: round(float(x[k])/dv,6) if x.get(k) not in (None,'') else None
for i in range(0,len(alvo),50):
  lote=alvo[i:i+50]
  batch=[{'method':'GET','relative_url':f"v21.0/{ACT}/insights?level=account&date_preset=maximum&fields={F}&filtering="+requests.utils.quote(json.dumps([{'field':'ad.id','operator':'IN','value':r['ads']}]))} for r in lote]
  for a in range(4):
    try:
      resp=requests.post('https://graph.facebook.com/',data={'access_token':T,'batch':json.dumps(batch)},timeout=180).json()
      if isinstance(resp,dict) and 'error' in resp: print(resp['error'].get('message')); time.sleep(20*(a+1)); continue
      break
    except Exception as e: print(e); time.sleep(10)
  for r,x in zip(lote,resp if isinstance(resp,list) else []):
    try: dado=(json.loads(x['body']).get('data') or [{}])[0] if x and x.get('code')==200 else {}
    except Exception: dado={}
    r['bm']={'cpm':f_(dado,'cpm'),'ctr_link':f_(dado,'inline_link_click_ctr',100),'ctr_all':f_(dado,'ctr',100),'cpc':f_(dado,'cost_per_inline_link_click')}
for c in d['cidades']:
  for r in c['criativos']: r.pop('ads',None)
json.dump(d,open('data.json','w'),ensure_ascii=False)
print(len(alvo),'criativos,',sum(1 for r in alvo if (r.get('bm') or {}).get('ctr_link') is not None),'com CTR do Meta')
