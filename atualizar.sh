#!/usr/bin/env bash
# Coleta tudo de novo (Meta, Guru, HubSpot) e gera index.html + site/index.html
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p raw
export TZ=America/Sao_Paulo
for s in allcamp ins metricas_bm adsets metricas_publico ads guru hs hs_subs build quadros metricas_criativo thumbs raio historico etickets vendas_planilha gerar; do
  echo "== $s"; python3 -u "$s.py"
done
