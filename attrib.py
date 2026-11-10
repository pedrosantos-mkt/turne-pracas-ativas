# Liga cada venda paga da Guru ao envio de formulário do comprador (mesma praça, antes da compra)
import json,unicodedata,collections,re
N=lambda s:unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().upper()
NZ=lambda s:N(s).replace(' ','').replace('-','').replace('_','')
subs=json.load(open('raw/hs_subs.json'))
adsets=json.load(open('raw/adsets.json')); ins=json.load(open('raw/ins.json'))
id2set={}; name2tag={}
from pracas import tag_of
import os
id2ad={}
if os.path.exists('raw/ads.json'):
  for v in json.load(open('raw/ads.json')).values():
    for a in v['ads']: id2ad[a['id']]=a['name']
CRE=re.compile(r'\[(IMG|VD|VID|CAR)\]')
for cid,rows in adsets.items():
  for r in rows:
    id2set[r['adset_id']]=(r['adset_name'],ins[cid]['name'])
CITYK={c:[p['cidade']]+p['aliases'] for c,p in json.load(open('raw/pracas.json')).items()}
by=collections.defaultdict(list)
for s in subs:
  if s.get('email'): by[s['email'].lower().strip()].append(s)
def norm_page(u):
  u=(u or '').split('?')[0].split('#')[0].replace('https://','').replace('http://','').rstrip('/')
  # Convocação Nacional: o anúncio leva para /l/<página> e o botão leva para /<página>, onde fica o formulário.
  # É o mesmo funil, então as duas viram uma linha só (e o domínio sem "ricardonunes." também).
  if u.endswith('convocacaonacional.com.br') or 'convocacaonacional.com.br/' in u:
    host,_,path=u.partition('/')
    if path.startswith('l/'): path=path[2:]
    u='ricardonunes.convocacaonacional.com.br/'+path if path else 'ricardonunes.convocacaonacional.com.br'
  return u or '(sem página)'
def attribute(email,city,ts):
  cand=[s for s in by.get(email,[]) if any(k in NZ(s['form'])+NZ(s['page']) for k in CITYK[city])]
  if not cand: return None
  before=[s for s in cand if s['at']<=ts*1000+3600e3]
  s=max(before or cand,key=lambda x:x['at'])
  # público: adset por ID numérico ou por nome, testando utm_term e utm_content
  adset=None;camp=s.get('utm_campaign') or ''
  for f in ('utm_term','utm_content'):
    v=(s.get(f) or '').strip()
    if not v or '{{' in v: continue
    if v.isdigit() and v in id2set: adset,camp=id2set[v]; break
    if not v.isdigit() and not re.match(r'\[(MV|MQV|C2G)',N(v)) : adset=v; break
  cre=None
  for f in ('utm_content','utm_term'):
    v=(s.get(f) or '').strip()
    if v.isdigit() and v in id2ad: cre=id2ad[v]; break
    if CRE.search(N(v)) and '{{' not in v: cre=v; break
  tag=tag_of(adset,camp) if adset else 'Sem UTM'
  return {'page':norm_page(s['page']),'tag':tag,'adset':adset,'cre':cre}
