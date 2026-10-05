// Funções compartilhadas entre o site (cliente) e o app (funcionário)
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const brl = v => Number(v).toLocaleString('pt-BR', {style:'currency', currency:'BRL'});
const dataBR = iso => iso ? iso.split('-').reverse().join('/') : '';
const val = id => ($('#'+id)?.value ?? '').trim();
const hojeISO = () => new Date(Date.now() - new Date().getTimezoneOffset()*60000).toISOString().slice(0,10);

async function api(url, {method='GET', body, codigo} = {}) {
  const r = await fetch('/api' + url, {
    method, credentials: 'same-origin',
    headers: {'Content-Type': 'application/json', ...(codigo ? {'X-Codigo': codigo} : {})},
    body: body ? JSON.stringify(body) : undefined
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(d.erro || 'Erro inesperado'), {status: r.status, data: d});
  return d;
}
const aviso = (m, ok=false) => `<div class="msg ${ok?'ok':''}" role="alert">${esc(m)}</div>`;
function mostrarErro(e) { const el = $('#erro'); if (el) el.innerHTML = aviso(e.message); else alert(e.message); }

const campo = (label, id, v='', type='text', extra='') =>
  `<label for="${id}">${label}</label><input id="${id}" type="${type}" value="${esc(v)}" ${extra}>`;

// bloco de campos de pessoa (cliente/funcionário). tipo: 'cliente' | 'funcionario'
function camposPessoa(d={}, tipo='cliente') {
  return campo('Nome completo', 'nome', d.nome, 'text', 'maxlength="200"') +
    campo('CPF (11 números)', 'cpf', d.cpf, 'text', 'inputmode="numeric" maxlength="11"') +
    campo('Data de nascimento', 'nascimento', d.nascimento, 'date') +
    `<div class="lin2"><div>${campo('Rua', 'rua', d.rua)}</div><div>${campo('Número', 'numero', d.numero, 'text', 'inputmode="numeric" maxlength="6"')}</div>
     <div>${campo('Bairro', 'bairro', d.bairro)}</div><div>${campo('Cidade', 'cidade', d.cidade)}</div></div>` +
    campo('Estado', 'estado', d.estado) +
    (tipo === 'cliente' ? campo('E-mail', 'email', d.email, 'email') : campo('Cargo', 'cargo', d.cargo)) +
    campo('Telefone com DDD (11 números)', 'telefone', d.telefone, 'text', 'inputmode="numeric" maxlength="11"');
}
function lerPessoa(tipo='cliente') {
  const o = {}; ['nome','cpf','nascimento','rua','numero','bairro','cidade','estado','telefone', tipo==='cliente'?'email':'cargo'].forEach(k => o[k] = val(k));
  return o;
}
const endereco = d => `${esc(d.rua)}, ${esc(d.numero)} - ${esc(d.bairro)}, ${esc(d.cidade)}/${esc(d.estado)}`;
const linha = (r, v) => `<p><b>${r}</b> ${v}</p>`;
