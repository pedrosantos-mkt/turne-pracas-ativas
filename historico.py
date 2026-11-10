# Praças encerradas: guarda o resultado final em cache/pracas/<código>.json (não muda mais)
# e junta todas as praças do ano no data.json antes do gerar.py.
import json, glob, os
os.makedirs('cache/pracas', exist_ok=True)
d = json.load(open('data.json')); PR = json.load(open('raw/pracas.json')); TODAS = json.load(open('raw/pracas_todas.json'))
novas = 0
for c in d['cidades']:
  p = TODAS.get(c['code'])
  if p and p['encerrada']:
    json.dump(c, open(f"cache/pracas/{c['code']}.json", 'w'), ensure_ascii=False); novas += 1
tem = {c['code'] for c in d['cidades']}
for f in glob.glob('cache/pracas/*.json'):
  c = json.load(open(f))
  if c['code'] in TODAS and c['code'] not in tem: d['cidades'].append(c); tem.add(c['code'])
for c in d['cidades']:
  c['encerrada'] = TODAS.get(c['code'], {}).get('encerrada', False); c['ciclo'] = TODAS.get(c['code'], {}).get('ciclo')
d['cidades'].sort(key=lambda c: (c['evento'], c['nome']))
json.dump(d, open('data.json', 'w'), ensure_ascii=False)
print(len(d['cidades']), 'praças no painel ·', novas, 'encerradas guardadas agora')
