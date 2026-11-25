"""Importa compras do PNCP para o banco.

Uso: python scripts/importar.py [AAAA-MM-DD] [limite_por_modalidade]
"""
import sys
from datetime import date, timedelta

from radar.infra.banco import engine
from radar.infra.pncp import ClientePNCP
from radar.servicos.importacao import ServicoImportacao
from radar.servicos.limpador import Limpador


def main() -> None:
    dia = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today() - timedelta(days=1)
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    ServicoImportacao(ClientePNCP(), Limpador(), engine).importar_periodo(dia, dia, limite)


if __name__ == "__main__":
    main()
