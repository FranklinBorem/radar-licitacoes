"""Consultas de contratações para o site (somente leitura)."""
from sqlalchemy import text

from radar.infra.banco import engine


class RepositorioContratacoes:
    def buscar(self, texto=None, municipio=None, modalidade=None,
               apenas_abertas=False, limite=20, deslocamento=0) -> list[dict]:
        condicoes, params = [], {"limite": limite, "deslocamento": deslocamento}
        if texto:  # procura no objeto da compra e na descrição dos itens
            condicoes.append(
                "(c.objeto ILIKE :texto OR EXISTS (SELECT 1 FROM item_contratacao i "
                "WHERE i.contratacao_id = c.id AND i.descricao ILIKE :texto))")
            params["texto"] = f"%{texto}%"
        if municipio:
            condicoes.append("u.municipio ILIKE :municipio")
            params["municipio"] = f"%{municipio}%"
        if modalidade:
            condicoes.append("c.modalidade_id = :modalidade")
            params["modalidade"] = modalidade
        if apenas_abertas:
            condicoes.append("c.situacao_id = 1 AND c.data_encerramento_proposta > now()")
        onde = "WHERE " + " AND ".join(condicoes) if condicoes else ""

        # 'onde' só junta trechos fixos escritos aqui; o que o usuário digita vai em params
        sql = text(f"""
            SELECT c.numero_controle_pncp, o.razao_social AS orgao, u.municipio,
                   c.modalidade_nome, c.objeto, c.valor_total_estimado,
                   c.data_encerramento_proposta
            FROM contratacao c
            JOIN orgao o ON o.cnpj = c.orgao_cnpj
            LEFT JOIN unidade_compradora u ON u.id = c.unidade_id
            {onde}
            ORDER BY c.data_publicacao_pncp DESC NULLS LAST, c.id DESC
            LIMIT :limite OFFSET :deslocamento""")
        with engine.connect() as conexao:
            return [dict(linha) for linha in conexao.execute(sql, params).mappings()]

    def obter(self, numero_controle: str) -> dict | None:
        with engine.connect() as conexao:
            compra = conexao.execute(text("""
                SELECT c.id, c.numero_controle_pncp, o.razao_social AS orgao, c.orgao_cnpj,
                       u.nome AS unidade, u.municipio, c.modalidade_nome, c.situacao_nome,
                       c.objeto, c.valor_total_estimado, c.valor_total_homologado,
                       c.data_publicacao_pncp, c.data_encerramento_proposta,
                       c.data_atualizacao_global, c.link_origem,
                       c.ano_compra, c.sequencial_compra
                FROM contratacao c
                JOIN orgao o ON o.cnpj = c.orgao_cnpj
                LEFT JOIN unidade_compradora u ON u.id = c.unidade_id
                WHERE c.numero_controle_pncp = :numero"""),
                {"numero": numero_controle}).mappings().first()
            if compra is None:
                return None
            compra = dict(compra)

            itens = [dict(i) | {"resultados": []} for i in conexao.execute(text("""
                SELECT id, numero_item, descricao, quantidade, unidade_medida,
                       valor_unitario_estimado
                FROM item_contratacao WHERE contratacao_id = :id ORDER BY numero_item"""),
                {"id": compra["id"]}).mappings()]
            por_id = {i["id"]: i for i in itens}

            for r in conexao.execute(text("""
                SELECT r.item_id, f.razao_social AS fornecedor, r.valor_unitario_homologado,
                       r.quantidade_homologada, r.ordem_classificacao
                FROM resultado_item r
                JOIN item_contratacao i ON i.id = r.item_id
                LEFT JOIN fornecedor f ON f.cnpj = r.fornecedor_cnpj
                WHERE i.contratacao_id = :id
                ORDER BY r.item_id, r.ordem_classificacao"""),
                {"id": compra["id"]}).mappings():
                por_id[r["item_id"]]["resultados"].append(dict(r))

        compra["itens"] = itens
        compra["link_pncp"] = (f"https://pncp.gov.br/app/editais/{compra['orgao_cnpj']}"
                               f"/{compra['ano_compra']}/{compra['sequencial_compra']}")
        return compra