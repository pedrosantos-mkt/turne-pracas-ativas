import json,collections,unicodedata,datetime as dt,re
g=json.load(open('raw/guru.json')); hs=json.load(open('raw/hs.json')); ins=json.load(open('raw/ins.json'))
N=lambda s:unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().upper().replace(' ','')
from pracas import guru_da_praca
PR=json.load(open('raw/pracas.json'))
BM=json.load(open('raw/metricas_bm.json'))
f_=lambda x,k,d=1: round(float(x[k])/d,6) if x.get(k) not in (None,'') else None
_QUAL_OLD={'200 mil a 499 mil por mês','500 mil a 999 mil por mês','1 milhão a 3 milhões por mês','3 milhões a 6 milhões por mês','Maior que 6 milhões por mês'}
def A(row,t,key='actions'):
  for a in row.get(key) or []:
    if a['action_type']==t: return float(a['value'])
  return 0
# venda da Guru -> campanha (pelo formulário do comprador; ver camp_attr.py). Namespace próprio: attrib.py redefine N.
CA={}; exec(open('attrib.py').read(),CA)
CA['id2cid']={r['adset_id']:cid for cid,rows in CA['adsets'].items() for r in rows}
exec(open('camp_attr.py').read(),CA)
out=[]
for code,pr in PR.items():
  nome,uf,ev,rota=pr['nome'],pr['uf'],pr['evento'],pr['rota']
  m=collections.Counter(); daily=collections.defaultdict(lambda:[0,0,0,0,0,0,0,0,0]); camps=[]
  for cid,v in ins.items():
    if v['city']!=code: continue
    cm=collections.Counter()
    for row in v['total'] or []:
      cm['spend']+=float(row['spend']); cm['imp']+=int(row['impressions']); cm['clk']+=int(row.get('inline_link_clicks',0))
      cm['lpv']+=A(row,'landing_page_view'); cm['ic']+=A(row,'initiate_checkout'); cm['pur']+=A(row,'purchase')
    m+=cm
    for row in v['daily'] or []:
      dd=daily[row['date_start']]; dd[0]+=float(row['spend']); dd[6]+=int(row.get('inline_link_clicks',0)); dd[7]+=A(row,'landing_page_view'); dd[8]+=int(row.get('impressions',0))
    if cm['spend']>0: camps.append({'id':cid,'name':v['name'],'status':v['status'],'spend':round(cm['spend'],2),'lpv':int(cm['lpv']),'pur':int(cm['pur'])})
  s=collections.Counter(); cargos=collections.defaultdict(collections.Counter)
  ing_c=collections.Counter(); fora=collections.Counter()
  for x in g:
    if x['status']!='approved': continue
    P=N(x['product']['name'])
    if not guru_da_praca(x['product']['name'],pr): continue
    O=N((x['product'].get('offer') or {}).get('name',''))+'|'+N(x['items'][0]['name'])+'|'+N(x['checkout_url'].split('/pay/')[-1])
    qty=sum(i.get('qty',1) for i in x['items']); tot=x['payment']['total'] or 0
    if 'CORTESIA' in P or 'CORTESIA' in O or tot==0: s['cort']+=qty; continue
    s['ing']+=qty; s['vendas']+=1; s['rec']+=tot
    d=dt.datetime.fromtimestamp(x['dates']['confirmed_at']).date().isoformat(); daily[d][1]+=qty; daily[d][4]+=tot; daily[d][5]+=1
    cg=hs.get((x['contact'].get('email') or '').lower().strip(),{}).get('ti__form____cargo') or 'Sem resposta'
    if re.search(r'CP[23]',O): cls_='qual'; daily[d][2]+=1
    elif 'CP1' in O: cls_='desq'; daily[d][3]+=1
    else: cls_='semcp'
    s[cls_]+=1  # qualificação por comprador (venda), não por ingresso: o 2º ingresso do duplo não declarou faturamento
    cargos[cg][cls_]+=1; cargos[cg]['vendas']+=1
    cid_,fora_=CA['camp_of']((x['contact'].get('email') or '').lower().strip(),code,x['dates']['confirmed_at'],x.get('trackings'))
    if cid_: ing_c[cid_]+=qty
    else: fora[fora_ or '']+=qty
  for c_ in camps: c_['ing']=ing_c.pop(c_['id'],0)
  for cid_,q in ing_c.items():  # venda ligada a campanha da praça sem gasto no período
    camps.append({'id':cid_,'name':ins[cid_]['name'],'status':ins[cid_]['status'],'spend':0,'lpv':0,'pur':0,'ing':q})
  extra=[{'name':n,'fora':True,'ing':q} for n,q in sorted(fora.items(),key=lambda t:-t[1]) if n]
  if fora.get(''): extra.append({'name':'Sem campanha identificada','semcamp':True,'ing':fora['']})
  start=min([d for d in daily if daily[d][0]>0] or [ev])
  days=sorted(d for d in daily if d>=start)
  bm=BM.get(code,{}); bt=bm.get('total',{}); bd=bm.get('dia',{})
  bm_tot={'cpm':f_(bt,'cpm'),'ctr_link':f_(bt,'inline_link_click_ctr',100),'ctr_all':f_(bt,'ctr',100),'cpc':f_(bt,'cost_per_inline_link_click')}
  out.append({'code':code,'nome':nome,'uf':uf,'evento':ev,'rota':rota,'inicio':start,
    'meta':{k2:round(v,2) for k2,v in m.items()},'guru':{k2:round(v,2) for k2,v in s.items()},
    'cargos':sorted([{'cargo':k2,**v} for k2,v in cargos.items()],key=lambda r:-r['vendas']),'bm':bm_tot,'daily':[[d,round(daily[d][0],2)]+[round(v,2) for v in daily[d][1:]]+[f_(bd.get(d,{}),'cpm'),f_(bd.get(d,{}),'inline_link_click_ctr',100),f_(bd.get(d,{}),'ctr',100)] for d in days],'camps':sorted(camps,key=lambda c:(-c['spend'],-c['ing'])),'camps_extra':extra})
json.dump({'gerado':dt.datetime.now().strftime('%d/%m/%Y %H:%M'),'cidades':out},open('data.json','w'),ensure_ascii=False)
for c in out: print(c['nome'],round(c['meta']['spend']),c['guru'],len(c['daily']),c['inicio'])
