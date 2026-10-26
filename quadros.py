# Quadros Público quente × frio e Páginas, por praça (roda depois do build.py)
import json,collections,re
exec(open('attrib.py').read())
g=json.load(open('raw/guru.json')); ads=json.load(open('raw/ads.json')); d=json.load(open('data.json'))
from pracas import guru_da_praca
PR=json.load(open('raw/pracas.json'))
def A(row,t):
  for a in row.get('actions') or []:
    if a['action_type']==t: return float(a['value'])
  return 0
def media(row):
  return collections.Counter({'spend':float(row['spend']),'imp':int(row['impressions']),'clk':int(row.get('inline_link_clicks',0)),'lpv':A(row,'landing_page_view'),'ic':A(row,'initiate_checkout'),'pur':A(row,'purchase')})
def ad_url(ad):
  cr=ad.get('creative') or {}
  urls=[u.get('website_url') for u in (cr.get('asset_feed_spec') or {}).get('link_urls',[]) if u.get('website_url')]
  oss=cr.get('object_story_spec') or {}
  urls+=[(oss.get('link_data') or {}).get('link'), ((oss.get('video_data') or {}).get('call_to_action') or {}).get('value',{}).get('link')]
  urls=[u for u in urls if u]
  return norm_page(urls[0]) if urls else '(sem URL)'
FIXP=lambda p:'(formulário embutido)' if 'hsforms' in p else p
for c in d['cidades']:
  code=c['code']; pr=PR[code]
  pub=collections.defaultdict(collections.Counter); pag=collections.defaultdict(collections.Counter); cre=collections.defaultdict(collections.Counter); prev={}; ids_cre={}
  for cid,v in ins.items():
    if v['city']!=code: continue
    for r in adsets.get(cid,[]): pub[tag_of(r['adset_name'],v['name'])]+=media(r)
    url={a['id']:ad_url(a) for a in ads.get(cid,{}).get('ads',[])}
    nome={a['id']:a['name'] for a in ads.get(cid,{}).get('ads',[])}
    for a in ads.get(cid,{}).get('ads',[]):
      cr_=a.get('creative') or {}
      link=a.get('preview_shareable_link') or cr_.get('instagram_permalink_url')
      if link and a['name'] not in prev: prev[a['name']]={'prev':link,'ad':a['id']}
    for r in ads.get(cid,{}).get('ins',[]):
      pag[url.get(r['ad_id'],'(sem URL)')]+=media(r); cre[nome.get(r['ad_id'],r['ad_id'])]+=media(r)
      ids_cre.setdefault(nome.get(r['ad_id'],r['ad_id']),[]).append(r['ad_id'])
  for x in g:
    if x['status']!='approved' or not (x['payment']['total'] or 0): continue
    P=NZ(x['product']['name'])
    if not guru_da_praca(x['product']['name'],pr) or 'CORTESIA' in P: continue
    O=NZ((x['product'].get('offer') or {}).get('name',''))+'|'+NZ(x['items'][0]['name'])+'|'+NZ(x['checkout_url'].split('/pay/')[-1])
    qty=sum(i.get('qty',1) for i in x['items'])
    cls_='qual' if re.search(r'CP[23]',O) else 'desq' if 'CP1' in O else 'semcp'
    a=attribute((x['contact'].get('email') or '').lower().strip(),code,x['dates']['confirmed_at']) or {'tag':'Sem UTM','page':'(sem formulário)','cre':None}
    for bucket,key in ((pub,a['tag']),(pag,FIXP(a['page'])))+(((cre,a['cre']),) if a['cre'] else ()):
      bucket[key]['ing']+=qty; bucket[key]['vendas']+=1; bucket[key][cls_]+=1
  ordem=['Quente','Frio','Mix validados','Sem tag','Sem UTM']
  MP=json.load(open('raw/metricas_publico.json')).get(code,{})
  f_=lambda x,k,d=1: round(float(x[k])/d,6) if x.get(k) not in (None,'') else None
  bmp={t:{'cpm':f_(x,'cpm'),'ctr_link':f_(x,'inline_link_click_ctr',100),'ctr_all':f_(x,'ctr',100),'cpc':f_(x,'cost_per_inline_link_click')} for t,x in MP.items()}
  c['publicos']=[{'nome':n,**{kk:round(vv,2) for kk,vv in pub[n].items()},'bm':bmp.get(n)} for n in ordem if n in pub]
  c['paginas']=sorted([{'nome':n,**{kk:round(vv,2) for kk,vv in v.items()}} for n,v in pag.items()],key=lambda r:(-r.get('spend',0),-r.get('ing',0)))
  c['criativos']=[{'nome':n,**{kk:round(vv,2) for kk,vv in v.items()},**prev.get(n,{}),'ads':ids_cre.get(n,[])} for n,v in cre.items() if v.get('spend',0)>0 or v.get('ing',0)>0]
json.dump(d,open('data.json','w'),ensure_ascii=False)
for c in d['cidades'][:2]:
  print(c['nome']); [print('  ',r) for r in c['publicos']]; [print('  ',r) for r in c['paginas']]
