# Liga uma venda da Guru a uma campanha do Meta da mesma praça.
# Ordem: conjunto pelo ID na UTM (utm_term/utm_content) -> utm_campaign (ID, ou nome parecido com o de hoje,
# porque a campanha pode ter sido renomeada depois do clique) -> tracking da própria Guru.
# Se a UTM aponta para uma campanha que não é da praça (ex.: campanha antiga de outra cidade), devolve o nome da UTM.
import re,difflib
AN=lambda s:re.sub(r'[^A-Z0-9]','',N(s))
def _spend(c): return sum(float(r['spend']) for r in ins[c]['total'] or [])
def _match(uc,code):
  uc=(uc or '').strip()
  if not uc or '{{' in uc: return None
  cids=[cid for cid,v in ins.items() if v['city']==code]
  if uc.isdigit(): return uc if uc in cids else None
  u=AN(uc)
  if len(u)<12: return None
  exact=[c for c in cids if AN(ins[c]['name'])==u]
  if exact: return max(exact,key=_spend)
  pref=[c for c in cids if AN(ins[c]['name']).startswith(u)]
  if pref: return max(pref,key=_spend)
  sc=sorted(((difflib.SequenceMatcher(None,u,AN(ins[c]['name'])).ratio(),_spend(c),c) for c in cids),reverse=True)
  if sc and sc[0][0]>=0.88: return sc[0][2]
  return None
def camp_of(email,code,ts,tracking=None):
  """devolve (campaign_id, None) | (None, nome_utm_de_fora) | (None, None)"""
  cand=[s for s in by.get(email,[]) if any(k in NZ(s['form'])+NZ(s['page']) for k in CITYK[code])]
  fora=None
  if cand:
    before=[s for s in cand if s['at']<=ts*1000+3600e3]
    s=max(before or cand,key=lambda y:y['at'])
    for f in ('utm_term','utm_content'):
      v=(s.get(f) or '').strip()
      if v.isdigit() and v in id2cid and ins.get(id2cid[v],{}).get('city')==code: return id2cid[v],None
    c=_match(s.get('utm_campaign'),code)
    if c: return c,None
    uc=(s.get('utm_campaign') or '').strip()
    if uc.startswith('[') and '{{' not in uc: fora=uc
  if isinstance(tracking,dict):
    c=_match(tracking.get('utm_campaign'),code)
    if c: return c,None
  return None,fora
