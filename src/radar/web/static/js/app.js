// JavaScript do site. Por enquanto, so preenche o ano no rodape.
document.addEventListener("DOMContentLoaded", () => {
  const ano = document.getElementById("ano");
  if (ano) ano.textContent = new Date().getFullYear();
});

// ---- Busca de contratações ----
const POR_PAGINA = 20;
let paginaAtual = 1;

const moeda = (v) => v == null ? "não informado"
  : Number(v).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const data = (d) => d ? new Date(d).toLocaleDateString("pt-BR") : "—";

function criar(tag, texto, classe) {
  const el = document.createElement(tag);
  if (texto != null) el.textContent = texto;
  if (classe) el.className = classe;
  return el;
}

async function buscar(pagina = 1) {
  const form = document.getElementById("filtros");
  if (!form) return;  // outras páginas não têm busca
  paginaAtual = pagina;
  const params = new URLSearchParams({ pagina });
  for (const [chave, valor] of new FormData(form)) if (valor) params.set(chave, valor);

  const status = document.getElementById("status");
  status.textContent = "Buscando...";
  try {
    const resposta = await fetch("/api/contratacoes?" + params);
    if (!resposta.ok) throw new Error(resposta.status);
    const compras = await resposta.json();

    const corpo = document.querySelector("#tabela tbody");
    corpo.replaceChildren();
    for (const c of compras) {
      const linha = document.createElement("tr");
      const objeto = c.objeto || "—";
      linha.append(
        criar("td", c.orgao), criar("td", c.municipio),
        criar("td", objeto.length > 160 ? objeto.slice(0, 160) + "…" : objeto),
        criar("td", moeda(c.valor_total_estimado)),
        criar("td", data(c.data_encerramento_proposta)),
      );
      const botao = criar("button", "Detalhes");
      botao.type = "button";
      botao.addEventListener("click", () => abrirDetalhe(c.numero_controle_pncp));
      const celula = document.createElement("td");
      celula.append(botao);
      linha.append(celula);
      corpo.append(linha);
    }
    status.textContent = compras.length ? "" : "Nenhuma compra encontrada.";
    document.getElementById("pagina").textContent = paginaAtual;
    document.getElementById("anterior").disabled = paginaAtual === 1;
    document.getElementById("proxima").disabled = compras.length < POR_PAGINA;
  } catch {
    status.textContent = "Não foi possível buscar. Tente de novo.";
  }
}

async function abrirDetalhe(numero) {
  const painel = document.getElementById("detalhe");
  const resposta = await fetch("/api/contratacoes/detalhe?" + new URLSearchParams({ numero }));
  if (!resposta.ok) return;
  const d = await resposta.json();

  painel.replaceChildren(
    criar("h2", d.orgao),
    criar("p", `${d.municipio ?? "—"} · ${d.modalidade_nome} · ${d.situacao_nome}`),
    criar("p", d.objeto),
    criar("p", `Valor estimado: ${moeda(d.valor_total_estimado)} · Encerra em: ${data(d.data_encerramento_proposta)}`),
  );

  const fonte = criar("p", null, "fonte");
  fonte.append("Fonte: ");
  const linkPncp = criar("a", "registro oficial no PNCP");
  linkPncp.href = d.link_pncp;
  linkPncp.target = "_blank";
  linkPncp.rel = "noopener";
  fonte.append(linkPncp, ` · atualizado no PNCP em ${data(d.data_atualizacao_global)}`);
  painel.append(fonte);

  const tabela = criar("table", null, "tabela");
  const cabecalho = document.createElement("tr");
  for (const nome of ["Nº", "Descrição", "Qtd", "Unidade", "Valor unit. estimado", "Resultado"])
    cabecalho.append(criar("th", nome));
  tabela.append(cabecalho);

  for (const item of d.itens) {
    const linha = document.createElement("tr");
    const resultado = item.resultados.length
      ? item.resultados.map((r) =>
          `${r.fornecedor ?? "fornecedor não identificado"}: ${moeda(r.valor_unitario_homologado)}`
        ).join(" | ")
      : "sem resultado";
    linha.append(
      criar("td", item.numero_item), criar("td", item.descricao),
      criar("td", item.quantidade), criar("td", item.unidade_medida),
      criar("td", moeda(item.valor_unitario_estimado)), criar("td", resultado),
    );
    tabela.append(linha);
  }
  const rolagem = criar("div", null, "rolagem");
  rolagem.append(tabela);
  painel.append(rolagem);
  painel.hidden = false;
  painel.scrollIntoView({ behavior: "smooth" });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("filtros");
  if (!form) return;
  form.addEventListener("submit", (e) => { e.preventDefault(); buscar(1); });
  document.getElementById("anterior").addEventListener("click", () => buscar(paginaAtual - 1));
  document.getElementById("proxima").addEventListener("click", () => buscar(paginaAtual + 1));
  buscar(1);
});