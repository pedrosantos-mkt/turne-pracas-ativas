# Vendas RGV da Planilha Comercial (aba Vendas): cidade na coluna L (Obs), cadeiras na D, valor na E.
# A planilha é privada; o resumo por cidade chega pelo segredo VENDAS_PLANILHA (ou ~/.config/turne/vendas_planilha.txt).
# Formato: CIDADE|E ou D|DD/MM da 1ª venda|vendas|cadeiras|receita em centenas de R$ ; ...
#   E = canal MDV (venda no evento) · D = resgate / outras ações depois do evento
# Cada grupo vai para o evento daquela cidade mais recente até a data da venda.
import json, os, datetime as dt
from pracas import NZ
txt = os.environ.get('VENDAS_PLANILHA') or (open(os.path.expanduser('~/.config/turne/vendas_planilha.txt')).read() if os.path.exists(os.path.expanduser('~/.config/turne/vendas_planilha.txt')) else '')
d = json.load(open('data.json')); TODAS = json.load(open('raw/pracas_todas.json'))
ano = dt.date.today().year
out = {}
for g in filter(None, (x.strip() for x in txt.split(';'))):
  cid, tipo, ddmm, n, cad, rec = g.split('|')
  c = NZ(cid).replace(' ', '')
  if not c: continue
  dv = dt.date(ano, int(ddmm[3:5]), int(ddmm[:2])).isoformat()
  evs = sorted((p for p in TODAS.values() if c in [p['cidade']] + p['aliases']), key=lambda p: p['evento'])
  if not evs: continue
  antes = [p for p in evs if p['evento'] <= dv]
  p = antes[-1] if antes else evs[0]
  k = out.setdefault(p['code'], {'evento': {'vendas': 0, 'cadeiras': 0, 'receita': 0}, 'depois': {'vendas': 0, 'cadeiras': 0, 'receita': 0}})['evento' if tipo == 'E' else 'depois']
  k['vendas'] += int(n); k['cadeiras'] += int(cad); k['receita'] += int(rec) * 100
for c in d['cidades']:
  if txt: c['planilha'] = out.get(c['code'])
  else: c.pop('planilha', None)   # sem a planilha: o painel avisa que as vendas não foram carregadas
json.dump(d, open('data.json', 'w'), ensure_ascii=False)
print(len(out), 'praças com vendas da planilha' if txt else 'sem VENDAS_PLANILHA: debriefing sem vendas')
for k, v in sorted(out.items()): print(' ', k, v['evento'], v['depois'])
