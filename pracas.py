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
  'CARAJAS': ('Carajás', 'PA'), 'ITAJAI': ('Itajaí', 'SC'), 'BRASILIA': ('Brasília', 'DF'), 'SAOPAULO': ('São Paulo', 'SP')}
# como a cidade aparece nos formulários e páginas do HubSpot
ALIASES = {'RIBEIRAOPRETO': ['RIBEIRAO'], 'CANOAS': ['CANOA'], 'BALNEARIOCAMBORIU': ['CAMBORIU', 'BALNEARIO'],
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

def data_evento(ddmm, hoje):
  d, m = map(int, ddmm.split('/'))
  ano = hoje.year + (1 if m < hoje.month - 3 else 0)
  return dt.date(ano, m, d)

def pracas(campanhas, hoje=None):
  """Praças com ao menos uma campanha de compra ativa; cada uma com todas as suas campanhas de compra do mesmo evento."""
  hoje = hoje or dt.date.today()
  ativas = {}
  for c in campanhas:
    p = parse(c['name'])
    if p and c.get('effective_status') == 'ACTIVE' and p[1]:
      ativas.setdefault(p[0], p)
  # campanha ativa sem data no nome herda a data de outra campanha ativa da cidade
  for c in campanhas:
    p = parse(c['name'])
    if p and c.get('effective_status') == 'ACTIVE' and p[0] not in ativas:
      outra = next((q for q in map(lambda x: parse(x['name']), campanhas) if q and q[0] == p[0] and q[1]), None)
      if outra: ativas[p[0]] = outra
  out = {}
  for cidade, (_, ddmm, rota) in ativas.items():
    ev = data_evento(ddmm, hoje)
    if ev < hoje - dt.timedelta(days=1): continue
    nome, uf = NOMES.get(cidade, (cidade.title(), ''))
    ini = (ev - dt.timedelta(days=120)).isoformat()
    def da_praca(c):
      p = parse(c['name'])
      if not p or p[0] != cidade: return False
      if p[1] == ddmm: return True
      # sem data no nome: mesma rota e começou na janela do evento
      return p[1] is None and p[2] == rota and ini <= (c.get('start_time') or '')[:10] <= ev.isoformat()
    ids = [c['id'] for c in campanhas if da_praca(c)]
    out[cidade] = {'code': cidade, 'nome': nome, 'uf': uf, 'evento': ev.isoformat(), 'rota': rota,
      'mes': MESES[ev.month - 1], 'aliases': ALIASES.get(cidade, [cidade]), 'campanhas': ids}
  return dict(sorted(out.items(), key=lambda kv: kv[1]['evento']))

def guru_da_praca(produto, p):
  """A venda (pelo nome do produto) é desta praça e deste evento?"""
  P = NZ(produto)
  return any(a in P for a in [p['code']] + p['aliases']) and p['mes'] in P
