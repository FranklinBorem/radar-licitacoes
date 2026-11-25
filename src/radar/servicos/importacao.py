"""Importacao: busca no PNCP, limpa os dados e grava no banco."""
from typing import ClassVar

from sqlalchemy.engine import Engine

from radar.infra.pncp import ClientePNCP
from radar.repositorios.importacao import RepositorioImportacao
from radar.servicos.limpador import Limpador


class ServicoImportacao:
    MODALIDADES: ClassVar[dict[int, str]] = {6: "Pregão Eletrônico", 8: "Dispensa"}

    def __init__(self, cliente: ClientePNCP, limpador: Limpador, engine: Engine):
        self.cliente = cliente
        self.L = limpador
        self.engine = engine

    def importar_periodo(self, inicio, fim, limite=None) -> dict[str, tuple[int, int]]:
        """Importa as compras do periodo. Devolve {modalidade: (gravadas, falhas)}."""
        resumo = {}
        for codigo, nome in self.MODALIDADES.items():
            ok = falhas = 0
            for compra in self.cliente.contratacoes(codigo, inicio, fim):
                if limite and ok + falhas >= limite:
                    break
                try:
                    # cada compra e gravada inteira ou nada (se der erro, desfaz tudo dela)
                    with self.engine.begin() as conexao:
                        self._importar_compra(compra, RepositorioImportacao(conexao))
                    ok += 1
                except Exception as erro:  # noqa: BLE001 - uma compra com erro nao para o resto
                    falhas += 1
                    print(f"  falhou {compra.get('numeroControlePNCP')}: {erro}")
                if (ok + falhas) % 10 == 0:
                    print(f"  {nome}: {ok} gravadas, {falhas} falhas...")
            print(f"{nome}: {ok} gravadas, {falhas} falhas")
            resumo[nome] = (ok, falhas)
        return resumo

    def _importar_compra(self, c: dict, repo: RepositorioImportacao) -> None:
        L = self.L
        org, uni = c["orgaoEntidade"], c.get("unidadeOrgao") or {}
        cnpj = L.so_digitos(org["cnpj"])

        repo.salvar_orgao({"cnpj": cnpj, "razao_social": org["razaoSocial"],
                           "esfera": org.get("esferaId"), "poder": org.get("poderId")})
        unidade_id = repo.salvar_unidade({
            "orgao_cnpj": cnpj, "codigo_unidade": uni.get("codigoUnidade"),
            "nome": uni.get("nomeUnidade"), "municipio": uni.get("municipioNome"),
            "codigo_ibge": uni.get("codigoIbge"), "uf": uni.get("ufSigla"),
        })
        ano, seq = c["anoCompra"], c["sequencialCompra"]
        contratacao_id = repo.salvar_contratacao({
            "numero_controle_pncp": c["numeroControlePNCP"],
            "orgao_cnpj": cnpj, "unidade_id": unidade_id,
            "ano_compra": ano, "sequencial_compra": seq,
            "numero_compra": c.get("numeroCompra"),
            "modalidade_id": c.get("modalidadeId"),
            "modalidade_nome": c.get("modalidadeNome"),
            "objeto": L.texto(c.get("objetoCompra")),
            "informacao_complementar": L.texto(c.get("informacaoComplementar")),
            "situacao_id": c.get("situacaoCompraId"),
            "situacao_nome": c.get("situacaoCompraNome"),
            "srp": c.get("srp"),
            "valor_total_estimado": L.valor_ou_vazio(c.get("valorTotalEstimado")),
            "valor_total_homologado": L.valor_ou_vazio(c.get("valorTotalHomologado")),
            "data_publicacao_pncp": c.get("dataPublicacaoPncp"),
            "data_abertura_proposta": c.get("dataAberturaProposta"),
            "data_encerramento_proposta": c.get("dataEncerramentoProposta"),
            "data_atualizacao_global": c.get("dataAtualizacaoGlobal"),
            "link_origem": L.link(c.get("linkSistemaOrigem")),
            "dados_brutos": c,
        })

        for it in self.cliente.itens(cnpj, ano, seq):
            catalogo = it.get("catalogoCodigoItem")
            item_id = repo.salvar_item({
                "contratacao_id": contratacao_id, "numero_item": it["numeroItem"],
                "descricao": L.descricao_item(it.get("descricao")),
                "material_ou_servico": it.get("materialOuServico"),
                "quantidade": it.get("quantidade"),
                "unidade_medida": it.get("unidadeMedida"),
                "valor_unitario_estimado": L.valor_ou_vazio(it.get("valorUnitarioEstimado")),
                "valor_total": L.valor_ou_vazio(it.get("valorTotal")),
                "codigo_catalogo": str(catalogo) if catalogo else None,
                "situacao_item_nome": it.get("situacaoCompraItemNome"),
                "tem_resultado": it.get("temResultado"),
            })
            if it.get("temResultado"):
                self._importar_resultados(cnpj, ano, seq, it["numeroItem"], item_id, repo)

    def _importar_resultados(self, cnpj, ano, seq, numero_item, item_id, repo) -> None:
        L = self.L
        for r in self.cliente.resultados(cnpj, ano, seq, numero_item):
            fornecedor = L.cnpj_pj(r.get("tipoPessoa"), r.get("niFornecedor"))
            if fornecedor:
                repo.salvar_fornecedor({
                    "cnpj": fornecedor, "razao_social": r.get("nomeRazaoSocialFornecedor"),
                    "porte": r.get("porteFornecedorNome"),
                    "natureza_juridica": r.get("naturezaJuridicaNome"),
                })
            repo.salvar_resultado({
                "item_id": item_id, "sequencial_resultado": r["sequencialResultado"],
                "fornecedor_cnpj": fornecedor,  # vazio para pessoa fisica
                "quantidade_homologada": r.get("quantidadeHomologada"),
                "valor_unitario_homologado": L.valor_ou_vazio(r.get("valorUnitarioHomologado")),
                "valor_total_homologado": L.valor_ou_vazio(r.get("valorTotalHomologado")),
                "percentual_desconto": r.get("percentualDesconto"),
                "ordem_classificacao": r.get("ordemClassificacaoSrp"),
                "data_resultado": r.get("dataResultado"),
                "situacao_nome": r.get("situacaoCompraItemResultadoNome"),
            })
