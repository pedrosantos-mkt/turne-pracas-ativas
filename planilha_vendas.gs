// Apps Script da Planilha Comercial (Extensões > Apps Script), publicado como App da Web.
// Devolve só o resumo das vendas da turnê por cidade e dia — sem nome, e-mail, telefone ou HubSpot.
// Formato de cada grupo: CIDADE|E ou D|DD/MM/AAAA|vendas|cadeiras|receita em centenas de R$ ; ...
//   E = canal MDV (venda no evento) · D = resgate / indicação / outras ações
// Aba Vendas: A = data, D = cadeiras (VENDA), E = valor (TICKET), I = canal, L = Obs (cidade).
function doGet() {
  const linhas = SpreadsheetApp.getActive().getSheetByName('Vendas').getDataRange().getValues().slice(1);
  const N = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase();
  const valor = v => typeof v === 'number' ? v : Number(String(v || '').replace(/[^\d,]/g, '').replace(',', '.')) || 0;
  const grupos = {};
  linhas.forEach(x => {
    const obs = N(x[11]), cad = Number(x[3]) || 0;
    const texto = String(x[0] || '').match(/^(\d{2}\/\d{2}\/\d{4})/);
    if (!/CNE|MDV/.test(obs) || !cad || !(x[0] instanceof Date || texto)) return;
    const cidade = obs.replace(/RESGATE|INDICACAO|CNE|MDV|VAI CANCELAR\?|CONTRATO NAO ASSINADO|[-\/]/g, ' ').replace(/\s+/g, ' ').trim();
    const dia = x[0] instanceof Date ? Utilities.formatDate(x[0], 'America/Sao_Paulo', 'dd/MM/yyyy') : texto[1];
    const k = [cidade, x[8] === 'MDV' ? 'E' : 'D', dia].join('|');
    const g = grupos[k] = grupos[k] || { n: 0, d: 0, e: 0 };
    g.n++; g.d += cad; g.e += valor(x[4]);
  });
  const txt = Object.keys(grupos).map(k => [k, grupos[k].n, grupos[k].d, Math.round(grupos[k].e / 100)].join('|')).join(';');
  return ContentService.createTextOutput(txt).setMimeType(ContentService.MimeType.TEXT);
}
