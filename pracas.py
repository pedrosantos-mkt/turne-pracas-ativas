# Praças ativas lidas dos nomes das campanhas de compra da conta MV, e tokens das APIs
import json, os, re, unicodedata, datetime as dt

def token(nome, arquivo):
  v = os.environ.get(nome)
  return v.strip() if v else open(os.path.expanduser(arquivo)).read().strip()

META_TOKEN = lambda: token('META_TOKEN', '~/.config/meta/token')
GURU_TOKEN = lambda: token('GURU_TOKEN', '~/.config/guru/token')
HUBSPOT_TOKEN = lambda: token('HUBSPOT_TOKEN', '~/.config/hubspot/token')

N = lambda s: unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().upper()
NZ = lambda s: re.sub(r'[\s\-_/.·]', '', N(s))

# nome de exibição e UF das praças já conhecidas; cidade nova cai no nome do token
NOMES = {'MANAUS': ('Manaus', 'AM'), 'BELEM': ('Belém', 'PA'), 'SINOP': ('Sinop', 'MT'), 'CUIABA': ('Cuiabá', 'MT'),
  'RIBEIRAOPRETO': ('Ribeirão Preto', 'SP'), 'PELOTAS': ('Pelotas', 'RS'), 'CANOAS': ('Canoas', 'RS'),
  'BALNEARIOCAMBORIU': ('Balneário Camboriú', 'SC'), 'FOZDOIGUACU': ('Foz do Iguaçu', 'PR'), 'CHAPECO': ('Chapecó', 'SC'),
  'MONTESCLAROS': ('Montes Claros', 'MG'), 'BELOHORIZONTE': ('Belo Horizonte', 'MG'), 'RECIFE': ('Recife', 'PE'),
  'CAMPINAS': ('Campinas', 'SP'), 'BARREIRAS': ('Barreiras', 'BA'), 'PARAGUAI': ('Paraguai', 'PY'),
  'CARAJAS': ('Carajás', 'PA'),
  'PALMAS': ('Palmas', 'TO'), 'FORTALEZA': ('Fortaleza', 'CE'), 'SALVADOR': ('Salvador', 'BA'), 'GOIANIA': ('Goiânia', 'GO'),
  'ARACAJU': ('Aracaju', 'SE'), 'JOAOPESSOA': ('João Pessoa', 'PB'), 'NATAL': ('Natal', 'RN'), 'MACEIO': ('Maceió', 'AL'),
  'CAMPOGRANDE': ('Campo Grande', 'MS'), 'IMPERATRIZ': ('Imperatriz', 'MA'), 'SAOLUIS': ('São Luís', 'MA'), 'TERESINA': ('Teresina', 'PI'),
  'LONDRINA': ('Londrina', 'PR'), 'MARINGA': ('Maringá', 'PR'), 'CASCAVEL': ('Cascavel', 'PR'), 'VITORIA': ('Vitória', 'ES'),
  'UBERLANDIA': ('Uberlândia', 'MG'), 'PORTOALEGRE': ('Porto Alegre', 'RS'), 'SANTAMARIA': ('Santa Maria', 'RS'),
  'CAXIASDOSUL': ('Caxias do Sul', 'RS'), 'POUSOALEGRE': ('Pouso Alegre', 'MG'), 'PASSOFUNDO': ('Passo Fundo', 'RS'),
  'CRICIUMA': ('Criciúma', 'SC'), 'FLORIANOPOLIS': ('Florianópolis', 'SC'), 'JOINVILLE': ('Joinville', 'SC'),
  'RONDONOPOLIS': ('Rondonópolis', 'MT'), 'RIOBRANCO': ('Rio Branco', 'AC'), 'DOURADOS': ('Dourados', 'MS'), 'CARUARU': ('Caruaru', 'PE'),
  'RIODEJANEIRO': ('Rio de Janeiro', 'RJ'), 'PONTAGROSSA': ('Ponta Grossa', 'PR'), 'CURITIBA': ('Curitiba', 'PR'),
  'PETROLINA': ('Petrolina', 'PE'), 'FEIRADESANTANA': ('Feira de Santana', 'BA'), 'JUIZDEFORA': ('Juiz de Fora', 'MG'),
  'SOROCABA': ('Sorocaba', 'SP'), 'MOSSORO': ('Mossoró', 'RN'), 'CAMPINAGRANDE': ('Campina Grande', 'PB'),
  'VITORIADACONQUISTA': ('Vitória da Conquista', 'BA'), 'ITAJAI': ('Itajaí', 'SC'), 'BRASILIA': ('Brasília', 'DF'), 'SAOPAULO': ('São Paulo', 'SP')}
# como a cidade aparece nos formulários e páginas do HubSpot
ALIASES = {'RIBEIRAOPRETO': ['RIBEIRAO'], 'FLORIANOPOLIS': ['FLORIPA'], 'CANOAS': ['CANOA'], 'BALNEARIOCAMBORIU': ['CAMBORIU', 'BALNEARIO'],
  'FOZDOIGUACU': ['FOZ'], 'MONTESCLAROS': ['MONTESCLAROS', 'MONTECLAROS'], 'PARAGUAI': ['PARAGUAI', 'CIUDADDELESTE']}
MESES = ['JANEIRO', 'FEVEREIRO', 'MARCO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']

def parse(nome):
  """(cidade, 'DD/MM' ou None, rota) de um nome de campanha de compra, ou None."""
  n = N(nome)
  if 'COMPRAS' not in n: return None
  m = re.search(r'\[80KM\]\s*\[([^\]]+)\]', n)
  if not m: return None
  cidade = NZ(m.group(1))
  dm = re.search(r'\[(\d{2}/\d{2})\]', n[m.end():]) or re.search(r'\[(\d{2}/\d{2})\]', n)
  r = re.search(r'RGV(\d{2})', n)
  return cidade, dm.group(1) if dm else None, int(r.group(1)) if r else None

# ciclos RGV (mesmas datas do painel do Perpétuo); a praça entra inteira no ciclo da data do evento
CICLOS = [(37, '2025-11-04', '2025-12-10'), (38, '2025-12-11', '2026-02-02'), (39, '2026-02-03', '2026-03-23'),
  (40, '2026-03-24', '2026-04-27'), (41, '2026-04-28', '2026-06-08'), (42, '2026-06-09', '2026-07-21'),
  (43, '2026-07-22', '2026-08-24'), (44, '2026-08-25', '2026-09-28'), (45, '2026-09-29', '2026-11-03'),
  (46, '2026-11-04', '2026-12-08')]
def ciclo_de(iso):
  return next((n for n, a, b in CICLOS if a <= iso <= b), None)

# praças do ano: eventos a partir desta data entram no painel (as encerradas ficam em cache/pracas/)
INICIO_ANO = '2026-01-01'
CANON = {'BALNEARIO': 'BALNEARIOCAMBORIU'}   # mesma cidade escrita de outro jeito no nome da campanha
FORA = {'REMARKETING'}

def data_evento(ddmm, ref):
  """data do evento 'DD/MM' perto da data de referência (início da campanha ou hoje)"""
  d, m = map(int, ddmm.split('/'))
  cands = [dt.date(ref.year + k, m, d) for k in (-1, 0, 1)]
  return min((c for c in cands if c >= ref - dt.timedelta(days=200)), key=lambda c: abs((c - ref).days))

def _ref(c):
  s = (c.get('start_time') or '')[:10]
  return dt.date.fromisoformat(s) if s else dt.date.today()

def todas_pracas(campanhas, hoje=None):
  """Todas as praças do ano lidas dos nomes das campanhas de compra; chave = CIDADE-DDMM (a mesma cidade pode ter vários eventos)."""
  hoje = hoje or dt.date.today()
  evs = {}
  for c in campanhas:
    p = parse(c['name'])
    if not p or not p[1]: continue
    cid = CANON.get(p[0], p[0])
    if cid in FORA: continue
    ev = data_evento(p[1], _ref(c))
    if ev.isoformat() < INICIO_ANO: continue
    k = (cid, ev)
    e = evs.setdefault(k, {'rota': p[2], 'campanhas': [], 'ativa': False})
    e['rota'] = e['rota'] or p[2]; e['campanhas'].append(c['id'])
    if c.get('effective_status') == 'ACTIVE': e['ativa'] = True
  # mesma cidade e rota com datas a até 20 dias uma da outra = o mesmo evento (data digitada diferente ou campanha avulsa,
  # ex.: Dourados 04/08 e 06/08, Vitória 01/06 e 17/06); fica a data com mais campanhas — a Guru não separa esses eventos
  for k in sorted(evs, key=lambda k: -len(evs[k]['campanhas'])):
    if k not in evs: continue
    for k2 in [k2 for k2 in evs if k2 != k and k2[0] == k[0] and evs[k2]['rota'] == evs[k]['rota'] and abs((k2[1] - k[1]).days) <= 20]:
      if len(evs[k2]['campanhas']) <= len(evs[k]['campanhas']):
        e2 = evs.pop(k2); evs[k]['campanhas'] += e2['campanhas']; evs[k]['ativa'] |= e2['ativa']
  # campanha sem data no nome: mesma cidade e rota, entra no evento seguinte ao início dela (até 120 dias)
  for c in campanhas:
    p = parse(c['name'])
    if not p or p[1]: continue
    cid = CANON.get(p[0], p[0]); ini = _ref(c)
    alvo = sorted((ev for (ci, ev), e in evs.items() if ci == cid and e['rota'] == p[2] and ini <= ev <= ini + dt.timedelta(days=120)))
    if alvo:
      e = evs[(cid, alvo[0])]; e['campanhas'].append(c['id'])
      if c.get('effective_status') == 'ACTIVE': e['ativa'] = True
  out = {}
  for (cid, ev), e in sorted(evs.items(), key=lambda kv: kv[0][1]):
    nome, uf = NOMES.get(cid, (cid.title(), ''))
    code = f"{cid}-{ev.strftime('%d%m')}"
    out[code] = {'code': code, 'cidade': cid, 'nome': nome, 'uf': uf, 'evento': ev.isoformat(), 'rota': e['rota'], 'ciclo': ciclo_de(ev.isoformat()),
      'mes': MESES[ev.month - 1], 'aliases': ALIASES.get(cid, [cid]), 'campanhas': e['campanhas'],
      'encerrada': ev < hoje - dt.timedelta(days=1), 'ativa': e['ativa']}
  return out

def pracas(campanhas, hoje=None, em_cache=()):
  """Praças a coletar agora: as que ainda não aconteceram + as encerradas do ano que não estão no cache."""
  return {k: p for k, p in todas_pracas(campanhas, hoje).items() if not p['encerrada'] or k not in em_cache}

# quente/frio pelo nome do público (ou tag na campanha)
def tag_of(adset,camp=''):
  a=N(adset); c=N(camp)
  if '[QUENTE]' in c or 'QUENTE' in a: return 'Quente'
  if '[FRIO]' in c or 'FRIO' in a: return 'Frio'
  if re.search(r'ENVOLVIMENTO|SEGUIDOR|\[PQ\]|SITE|ENGAJ|VISITANTE|COMPRADORES|LISTA|BASE',a): return 'Quente'
  if re.search(r'SEMELHANT|INTERESSE|ADVANT|ADVTG|ADVANTGE|\[PF\]|ABERTO|BROAD|LAL',a): return 'Frio'
  if 'MIX' in a or 'VALIDADO' in a: return 'Mix validados'
  return 'Sem tag'

_TODAS = None
_CACHE_VENDA = {}
def _todas():
  global _TODAS
  if _TODAS is None: _TODAS = list(json.load(open('raw/pracas_todas.json')).values())
  return _TODAS

def praca_da_venda(x):
  """Código da praça de uma venda da Guru: cidade no nome do produto (a mais específica), mês do nome quando houver,
  e o evento dessa cidade logo depois da compra (a mesma cidade tem vários eventos no ano)."""
  key = x.get('id') or id(x)
  if key in _CACHE_VENDA: return _CACHE_VENDA[key]
  P = NZ(x['product']['name']); res = None
  best = max(((len(a), p['cidade']) for p in _todas() for a in [p['cidade']] + p['aliases'] if a in P), default=None)
  if best:
    evs = [p for p in _todas() if p['cidade'] == best[1]]
    mes = [m for m in MESES if m in P]
    if mes: evs = [p for p in evs if p['mes'] in mes] or []
    ts = (x.get('dates') or {}).get('confirmed_at') or (x.get('dates') or {}).get('ordered_at')
    dv = dt.datetime.fromtimestamp(ts).date().isoformat() if isinstance(ts, (int, float)) else None
    if evs and dv:
      prox = [p for p in evs if p['evento'] >= dv]
      res = (min(prox, key=lambda p: p['evento']) if prox else max(evs, key=lambda p: p['evento']))['code']
      # venda muito antes do evento (mais de 150 dias) é de outra edição
      if dt.date.fromisoformat(next(p for p in evs if p['code'] == res)['evento']) - dt.date.fromisoformat(dv) > dt.timedelta(days=150): res = None
  _CACHE_VENDA[key] = res
  return res

def guru_da_praca(x, p):
  """A venda da Guru é desta praça (deste evento)?"""
  return praca_da_venda(x) == p['code']
