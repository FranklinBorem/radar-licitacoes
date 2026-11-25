"""Gravacao no banco dos dados coletados do PNCP."""
import json
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.engine import Connection

COLUNAS_JSON = {"dados_brutos"}


class RepositorioImportacao:
    """Grava com 'upsert': insere se for novo, atualiza se ja existe.

    Recebe uma conexao aberta. Quem chama decide quando confirmar ou desfazer.
    """

    def __init__(self, conexao: Connection):
        self.conexao = conexao

    def _upsert(self, tabela: str, dados: dict, conflito: list, retorna_id: bool = False):
        colunas = list(dados)
        valores = ", ".join(
            f"CAST(:{c} AS jsonb)" if c in COLUNAS_JSON else f":{c}" for c in colunas
        )
        atualiza = ", ".join(f"{c} = EXCLUDED.{c}" for c in colunas if c not in conflito)
        sql = (
            f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({valores}) "
            f"ON CONFLICT ({', '.join(conflito)}) DO UPDATE SET {atualiza}"
        )
        if retorna_id:
            sql += " RETURNING id"
        parametros = {
            c: json.dumps(v, ensure_ascii=False) if c in COLUNAS_JSON else v
            for c, v in dados.items()
        }
        resultado = self.conexao.execute(text(sql), parametros)
        return resultado.scalar_one() if retorna_id else None

    def salvar_orgao(self, dados: dict) -> None:
        self._upsert("orgao", dados, ["cnpj"])

    def salvar_unidade(self, dados: dict) -> int:
        return self._upsert("unidade_compradora", dados,
                            ["orgao_cnpj", "codigo_unidade"], retorna_id=True)

    def salvar_contratacao(self, dados: dict) -> int:
        dados = {**dados, "coletado_em": datetime.now(UTC)}
        return self._upsert("contratacao", dados, ["numero_controle_pncp"], retorna_id=True)

    def salvar_item(self, dados: dict) -> int:
        return self._upsert("item_contratacao", dados,
                            ["contratacao_id", "numero_item"], retorna_id=True)

    def salvar_fornecedor(self, dados: dict) -> None:
        self._upsert("fornecedor", dados, ["cnpj"])

    def salvar_resultado(self, dados: dict) -> None:
        self._upsert("resultado_item", dados, ["item_id", "sequencial_resultado"])
