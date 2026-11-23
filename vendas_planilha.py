# Vendas RGV da Planilha Comercial (aba Vendas): cidade na coluna L (Obs), cadeiras na D, valor na E.
# A planilha é privada; o resumo por cidade chega pelo segredo VENDAS_PLANILHA (ou ~/.config/turne/vendas_planilha.txt).
# Formato: CIDADE|E ou D|DD/MM/AAAA (ou DD/MM da 1ª venda)|vendas|cadeiras|receita em centenas de R$ ; ...
#   E = canal MDV (venda no evento) · D = resgate / outras ações depois do evento
# Cada grupo vai para o evento daquela cidade mais recente até a data da venda.
import json, os, datetime as dt
from pracas import NZ
import requests
def da_planilha():
  """resumo ao vivo pelo Apps Script da planilha (segredo VENDAS_URL); sem ele, o resumo guardado em VENDAS_PLANILHA"""
  url = os.environ.get('VENDAS_URL')
  if not url: return None
  for t in range(4):
    try:
      r = requests.get(url, timeout=60)
      if r.status_code == 200 and '|' in r.text and '<html' not in r.text[:200].lower(): return r.text
      print('planilha respondeu', r.status_code)
    except Exception as e: print('planilha:', type(e).__name__)
  raise SystemExit('Apps Script da planilha não respondeu; nada é publicado nesta rodada')
txt = da_planilha() or os.environ.get('VENDAS_PLANILHA') or (open(os.path.expanduser('~/.config/turne/vendas_planilha.txt')).read() if os.path.exists(os.path.expanduser('~/.config/turne/vendas_planilha.txt')) else '')
d = json.load(open('data.json')); TODAS = json.load(open('raw/pracas_todas.json'))
ano = dt.date.today().year
out = {}
for g in filter(None, (x.strip() for x in txt.split(';'))):
  cid, tipo, ddmm, n, cad, rec = g.split('|')
  c = NZ(cid).replace(' ', '')
  if not c: continue
  dv = dt.date(int(ddmm[6:10]) if len(ddmm) >= 10 else ano, int(ddmm[3:5]), int(ddmm[:2])).isoformat()   # DD/MM/AAAA (Apps Script) ou DD/MM (resumo antigo)
  # cidade escrita livre na coluna L ("Balneário e Itajaí", "Juiz de fora"): vale o nome/apelido de praça mais longo contido nela
  mel = max(((len(a), p['cidade']) for p in TODAS.values() for a in [p['cidade']] + p['aliases'] if a and a in c), default=None)
  evs = sorted((p for p in TODAS.values() if mel and p['cidade'] == mel[1]), key=lambda p: p['evento'])
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
