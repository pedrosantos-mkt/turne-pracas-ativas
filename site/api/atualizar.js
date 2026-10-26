// Botão "Atualizar agora": GET devolve o estado da última rodada; POST dispara o workflow no GitHub.
const REPO = process.env.GH_REPO;            // ex.: dono/turne-pracas-ativas
const TOKEN = process.env.GH_DISPATCH_TOKEN; // token com permissão de Actions só neste repositório
const WF = 'atualizar.yml';

async function gh(path, init = {}) {
  const r = await fetch(`https://api.github.com/repos/${REPO}${path}`, {
    ...init,
    headers: { Authorization: `Bearer ${TOKEN}`, Accept: 'application/vnd.github+json', 'User-Agent': 'turne-pracas-ativas', ...(init.headers || {}) },
  });
  if (!r.ok && r.status !== 204) throw new Error(`GitHub ${r.status}`);
  return r.status === 204 ? null : r.json();
}

async function ultima() {
  const j = await gh(`/actions/workflows/${WF}/runs?per_page=1`);
  const run = j.workflow_runs[0];
  return run ? { status: run.status, conclusion: run.conclusion, inicio: run.run_started_at || run.created_at, fim: run.updated_at } : null;
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (!REPO || !TOKEN) return res.status(500).json({ erro: 'Atualização sob demanda não configurada.' });
  try {
    const run = await ultima();
    if (req.method === 'POST') {
      if (run && run.status !== 'completed') return res.status(202).json({ rodando: true, run });
      // intervalo mínimo entre pedidos, para ninguém gastar a cota do GitHub apertando o botão em sequência
      const desde = run ? (Date.now() - Date.parse(run.fim)) / 60000 : Infinity;
      if (desde < 30) return res.status(429).json({ erro: `Os dados foram atualizados há ${Math.round(desde)} min. Dá para pedir de novo em ${Math.ceil(30 - desde)} min.` });
      await gh(`/actions/workflows/${WF}/dispatches`, { method: 'POST', body: JSON.stringify({ ref: 'main' }), headers: { 'Content-Type': 'application/json' } });
      return res.status(202).json({ rodando: true, disparado: true });
    }
    return res.status(200).json({ rodando: !!run && run.status !== 'completed', run });
  } catch (e) {
    return res.status(502).json({ erro: 'Não consegui falar com o GitHub agora. Tente de novo em alguns minutos.' });
  }
};
