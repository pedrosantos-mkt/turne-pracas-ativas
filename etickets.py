# Comparecimento (check-in) de cada praça a partir do dia seguinte ao evento: e-tickets da Guru
# pagos × cortesia. Fica guardado na praça (cache/pracas/) e não é buscado de novo.
import requests, json, base64, time, datetime as dt, os, glob
from pracas import GURU_TOKEN, NZ
H = {'Authorization': 'Bearer ' + GURU_TOKEN(), 'Accept': 'application/json',
     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'}
URL = 'https://digitalmanager.guru/api/v2/etickets'
d = json.load(open('data.json')); TODAS = json.load(open('raw/pracas_todas.json'))
hoje = dt.date.today()
JAN = 3   # data da campanha pode diferir 1 dia da data real do evento (Imperatriz, Pouso Alegre, Criciúma, Juiz de Fora)
VERSAO = 2
alvo = [c for c in d['cidades'] if c.get('checkin_v') != VERSAO and dt.date.fromisoformat(c['evento']) <= hoje - dt.timedelta(days=1)]   # aparece no dia seguinte; refaz até a janela fechar

def pagina(cur):
  for t in range(10):
    r = requests.get(URL, headers=H, params={'cursor': cur} if cur else {}, timeout=(10, 60))
    if r.status_code == 429: time.sleep(min(120, 10 * (t + 1))); continue
    if r.status_code != 200: raise SystemExit(f'Guru e-tickets: {r.status_code}')
    return r.json()
  raise SystemExit('Guru e-tickets: sem resposta')

def janela(ev):
  """e-tickets com início entre ev-JAN e ev+JAN (a lista vem do mais novo ao mais antigo)"""
  ini, fim = ev - dt.timedelta(days=JAN), ev + dt.timedelta(days=JAN)
  cur = base64.b64encode(json.dumps({'start_at': (fim + dt.timedelta(days=1)).isoformat(), 'id': 0, '_pointsToNextItems': True}).encode()).decode()
  out = []
  while True:
    j = pagina(cur); dados = j.get('data', [])
    for e in dados:
      dia = dt.datetime.fromtimestamp(e['start_at']).date() if e.get('start_at') else None
      if dia and ini <= dia <= fim: out.append((dia, e))
    if not dados or not j.get('has_more_pages'): return out
    ult = dt.datetime.fromtimestamp(dados[-1]['start_at']).date() if dados[-1].get('start_at') else ini
    if ult < ini: return out
    cur = j.get('next_cursor')

cache_jan = {}
for c in alvo:
  ev = dt.date.fromisoformat(c['evento'])
  if ev not in cache_jan: cache_jan[ev] = janela(ev)
  p = TODAS.get(c['code'], {}); chaves = [p.get('cidade', '')] + p.get('aliases', [])
  perto = lambda q: abs((dt.date.fromisoformat(q['evento']) - ev).days) <= 2 * JAN
  outras = [a for q in TODAS.values() if q['code'] != c['code'] and q['cidade'] != p.get('cidade') and perto(q) for a in [q['cidade']] + q['aliases']]
  minhas = []
  for dia, e in cache_jan[ev]:
    P = NZ(e.get('product_name'))
    m = max((len(a) for a in chaves if a in P), default=0)
    if not m or any(len(a) > m and a in P for a in outras): continue   # outra praça perto (ex.: Vitória × Vitória da Conquista)
    minhas.append((dia, e, P))
  # data real do evento = dia com mais e-tickets da cidade na janela (sobra de VIP/cortesia em outro dia fica fora)
  dias = {}
  for dia, _, _ in minhas: dias[dia] = dias.get(dia, 0) + 1
  real = max(dias, key=dias.get) if dias else None
  r = {'pago': {'emitidos': 0, 'presentes': 0}, 'cortesia': {'emitidos': 0, 'presentes': 0}, 'cancelados': 0, 'data': real.isoformat() if real else None}
  for dia, e, P in minhas:
    if dia != real: continue
    if e.get('status') == 'canceled': r['cancelados'] += 1; continue
    t = 'cortesia' if 'CORTESIA' in P else 'pago'
    r[t]['emitidos'] += 1; r[t]['presentes'] += e.get('status') == 'checked_in'
  c['checkin'] = r if real else None
  if ev <= hoje - dt.timedelta(days=JAN + 1): c['checkin_v'] = VERSAO
  print(c['code'], r)
  if os.path.exists(f"cache/pracas/{c['code']}.json"): json.dump(c, open(f"cache/pracas/{c['code']}.json", 'w'), ensure_ascii=False)
json.dump(d, open('data.json', 'w'), ensure_ascii=False)
print(len(alvo), 'praças com comparecimento novo')
