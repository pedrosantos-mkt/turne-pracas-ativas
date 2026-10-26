# Raio de cada praça: localização dos conjuntos de anúncios no Meta → municípios cobertos (IBGE) e cidade dos compradores (Guru)
import json, csv, math, requests, time, collections
from pracas import META_TOKEN, N, NZ, guru_da_praca
T=META_TOKEN()
d=json.load(open('data.json')); adsets=json.load(open('raw/adsets.json')); ins=json.load(open('raw/ins.json'))
PR=json.load(open('raw/pracas.json')); g=json.load(open('raw/guru.json'))
_est=list(csv.DictReader(open('ref/estados.csv',encoding='utf-8-sig')))
uf_de={NZ(r['nome']):(r['uf'],r['codigo_uf']) for r in _est}
UF=lambda regiao: uf_de.get(NZ((regiao or '').replace('(state)','').replace('(estado)','')),('',''))[0]
# cidades fora do Brasil usadas como centro
EXTERIOR={'CIUDADDELESTE':(-25.5097,-54.6111,'PY')}
cod_uf={r['codigo_uf']:r['uf'] for r in _est}
pop={s['localidade']['id']:int(s['serie']['2022']) for s in json.load(open('ref/populacao_2022.json'))[0]['resultados'][0]['series']}
MUN=[{'nome':r['nome'],'uf':cod_uf[r['codigo_uf']],'lat':float(r['latitude']),'lon':float(r['longitude']),'pop':pop.get(r['codigo_ibge'],0)} for r in csv.DictReader(open('ref/municipios.csv',encoding='utf-8'))]
por_nome={(NZ(m['nome']),m['uf']):m for m in MUN}
def dist(a,b,c,e):
  p=math.pi/180; x=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((e-b)*p/2)**2
  return 12742*math.asin(math.sqrt(x))
# segmentação de todos os conjuntos das praças, em lotes de IDs
ids=[r['adset_id'] for rows in adsets.values() for r in rows]
alvo={}
for i in range(0,len(ids),40):
  for a in range(4):
    r=requests.get('https://graph.facebook.com/v21.0/',params={'access_token':T,'ids':','.join(ids[i:i+40]),'fields':'effective_status,targeting{geo_locations}'},timeout=90).json()
    if 'error' not in r: alvo.update(r); break
    print(r['error'].get('message')); time.sleep(15*(a+1))
cidade_do_conjunto={r['adset_id']:ins[cid]['city'] for cid,rows in adsets.items() for r in rows}
gasto_do_conjunto={r['adset_id']:float(r['spend']) for rows in adsets.values() for r in rows}
for c in d['cidades']:
  centros={}
  for aid,info in alvo.items():
    if cidade_do_conjunto.get(aid)!=c['code']: continue
    geo=(info.get('targeting') or {}).get('geo_locations') or {}
    for ct in geo.get('cities',[]):
      uf=UF(ct.get('region')); m=por_nome.get((NZ(ct['name']),uf))
      if not m and NZ(ct['name']) in EXTERIOR:
        la,lo,uf=EXTERIOR[NZ(ct['name'])]; m={'lat':la,'lon':lo}
      k=('cidade',ct['name'],uf,ct.get('radius'))
      e=centros.setdefault(k,{'tipo':'cidade','nome':ct['name'],'uf':uf,'raio_km':ct.get('radius') if ct.get('distance_unit','kilometer')=='kilometer' else round((ct.get('radius') or 0)*1.609),'lat':m and m['lat'],'lon':m and m['lon'],'conjuntos':0,'ativos':0,'gasto':0})
      e['conjuntos']+=1; e['ativos']+=info.get('effective_status')=='ACTIVE'; e['gasto']+=gasto_do_conjunto.get(aid,0)
    for cl in geo.get('custom_locations',[]):
      k=('ponto',round(float(cl['latitude']),3),round(float(cl['longitude']),3),cl.get('radius'))
      raio=cl.get('radius') if cl.get('distance_unit','kilometer')=='kilometer' else round((cl.get('radius') or 0)*1.609)
      perto=min(MUN,key=lambda m:dist(float(cl['latitude']),float(cl['longitude']),m['lat'],m['lon']))
      e=centros.setdefault(k,{'tipo':'ponto','nome':cl.get('name') or ('Ponto perto de '+perto['nome']),'uf':'' if cl.get('name') else perto['uf'],'raio_km':raio,'lat':float(cl['latitude']),'lon':float(cl['longitude']),'conjuntos':0,'ativos':0,'gasto':0})
      e['conjuntos']+=1; e['ativos']+=info.get('effective_status')=='ACTIVE'; e['gasto']+=gasto_do_conjunto.get(aid,0)
    for rg in geo.get('regions',[]):
      e=centros.setdefault(('estado',rg.get('name')),{'tipo':'estado','nome':rg.get('name'),'uf':UF(rg.get('name')),'raio_km':None,'lat':None,'lon':None,'conjuntos':0,'ativos':0,'gasto':0})
      e['conjuntos']+=1; e['ativos']+=info.get('effective_status')=='ACTIVE'; e['gasto']+=gasto_do_conjunto.get(aid,0)
  cs=sorted(centros.values(),key=lambda e:-e['gasto'])
  # municípios dentro de algum raio
  dentro={}
  for e in cs:
    if e['lat'] is None or not e['raio_km']: continue
    for m in MUN:
      km=dist(e['lat'],e['lon'],m['lat'],m['lon'])
      if km<=e['raio_km']:
        k=(m['nome'],m['uf']); dentro[k]=min(dentro.get(k,(1e9,m))[0],km),m
  # cidade informada pelo comprador na Guru (vendas pagas da praça)
  comp=collections.Counter()
  for x in g:
    if x['status']!='approved' or not (x['payment']['total'] or 0) or not guru_da_praca(x['product']['name'],PR[c['code']]): continue
    if 'CORTESIA' in NZ(x['product']['name']): continue
    ct=x.get('contact') or {}; comp[(NZ(ct.get('address_city')),(ct.get('address_state') or '').upper()[:2])]+=1
  muns=[]
  for (nome,uf),(km,m) in dentro.items():
    muns.append({'nome':nome,'uf':uf,'km':round(km),'pop':m['pop'],'lat':round(m['lat'],3),'lon':round(m['lon'],3),'compradores':comp.pop((NZ(nome),uf),0)})
  muns.sort(key=lambda r:(-r['compradores'],-r['pop']))
  sem=comp.pop(('',''),0)
  fora=[]
  for (nz,uf),n in comp.most_common():
    m=por_nome.get((nz,uf)); fora.append({'nome':m['nome'] if m else nz.title(),'uf':uf,'compradores':n,'pop':m and m['pop'],'lat':m and round(m['lat'],3),'lon':m and round(m['lon'],3),'km':round(dist(cs[0]['lat'],cs[0]['lon'],m['lat'],m['lon'])) if (m and cs and cs[0]['lat'] is not None) else None})
  c['raio']={'centros':cs,'municipios':muns,'fora':fora,'sem_cidade':sem}
json.dump(d,open('data.json','w'),ensure_ascii=False)
for c in d['cidades']:
  r=c['raio']; dentro_c=sum(m['compradores'] for m in r['municipios']); fora_c=sum(m['compradores'] for m in r['fora'])
  print(c['nome'],[(e['nome'],e['raio_km'],e['conjuntos']) for e in r['centros']],len(r['municipios']),'mun.',sum(m['pop'] for m in r['municipios']),'hab | compradores dentro',dentro_c,'fora',fora_c,'sem',r['sem_cidade'])
