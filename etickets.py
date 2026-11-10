# Comparecimento (check-in) de cada praça a partir do dia seguinte ao evento: e-tickets da Guru
# pagos × cortesia. Fica guardado na praça (cache/pracas/) e não é buscado de novo.
import requests, json, base64, time, datetime as dt, os, glob
from pracas import GURU_TOKEN, NZ
H = {'Authorization': 'Bearer ' + GURU_TOKEN(), 'Accept': 'application/json',
     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'}
URL = 'https://digitalmanager.guru/api/v2/etickets'
d = json.load(open('data.json')); TODAS = json.load(open('raw/pracas_todas.json'))
hoje = dt.date.today()
alvo = [c for c in d['cidades'] if 'checkin' not in c and dt.date.fromisoformat(c['evento']) <= hoje - dt.timedelta(days=1)]

def pagina(cur):
  for t in range(10):
    r = requests.get(URL, headers=H, params={'cursor': cur} if cur else {}, timeout=(10, 60))
    if r.status_code == 429: time.sleep(min(120, 10 * (t + 1))); continue
    if r.status_code != 200: raise SystemExit(f'Guru e-tickets: {r.status_code}')
    return r.json()
  raise SystemExit('Guru e-tickets: sem resposta')

def do_dia(ev):
  """e-tickets com início no dia do evento (a lista vem do mais novo ao mais antigo; o cursor começa no dia seguinte)"""
  cur = base64.b64encode(json.dumps({'start_at': (ev + dt.timedelta(days=1)).isoformat(), 'id': 0, '_pointsToNextItems': True}).encode()).decode()
  out = []
  while True:
    j = pagina(cur); dados = j.get('data', [])
    for e in dados:
      dia = dt.datetime.fromtimestamp(e['start_at']).date() if e.get('start_at') else None
      if dia == ev: out.append(e)
    if not dados or not j.get('has_more_pages'): return out
    ult = dt.datetime.fromtimestamp(dados[-1]['start_at']).date() if dados[-1].get('start_at') else ev
    if ult < ev: return out
    cur = j.get('next_cursor')

por_dia = {}
for c in alvo:
  ev = dt.date.fromisoformat(c['evento'])
  if ev not in por_dia: por_dia[ev] = do_dia(ev)
  p = TODAS.get(c['code'], {}); chaves = [p.get('cidade', '')] + p.get('aliases', [])
  outras = [a for q in TODAS.values() if q['evento'] == c['evento'] and q['code'] != c['code'] for a in [q['cidade']] + q['aliases']]
  r = {'pago': {'emitidos': 0, 'presentes': 0}, 'cortesia': {'emitidos': 0, 'presentes': 0}}
  for e in por_dia[ev]:
    P = NZ(e.get('product_name'))
    m = max((len(a) for a in chaves if a in P), default=0)
    if not m or any(len(a) > m and a in P for a in outras): continue   # outra praça no mesmo dia (ex.: Vitória × Vitória da Conquista)
    if e.get('status') == 'canceled': continue
    t = 'cortesia' if 'CORTESIA' in P else 'pago'
    r[t]['emitidos'] += 1; r[t]['presentes'] += e.get('status') == 'checked_in'
  c['checkin'] = r if r['pago']['emitidos'] + r['cortesia']['emitidos'] else None
  print(c['code'], r)
  if os.path.exists(f"cache/pracas/{c['code']}.json"): json.dump(c, open(f"cache/pracas/{c['code']}.json", 'w'), ensure_ascii=False)
json.dump(d, open('data.json', 'w'), ensure_ascii=False)
print(len(alvo), 'praças com comparecimento novo')
