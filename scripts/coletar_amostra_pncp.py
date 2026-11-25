import json
from datetime import date, timedelta
from pathlib import Path

import httpx

URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
# O PNCP bloqueia quem não manda esses cabeçalhos
CABECALHOS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}
MODALIDADES = {6: "Pregão Eletrônico", 8: "Dispensa"}


class ClientePNCP:
    """Conversa com a API do PNCP."""

    def buscar_pagina(self, modalidade: int, inicio: date, fim: date, pagina: int = 1) -> dict:
        parametros = {
            "dataInicial": inicio.strftime("%Y%m%d"),  # formato AAAAMMDD
            "dataFinal": fim.strftime("%Y%m%d"),
            "codigoModalidadeContratacao": modalidade,  # obrigatório
            "uf": "MG",
            "pagina": pagina,
            "tamanhoPagina": 50,  # mínimo aceito é 10
        }
        resposta = httpx.get(URL, params=parametros, headers=CABECALHOS, timeout=60)
        resposta.raise_for_status()
        return resposta.json()


def main():
    fim = date.today()
    inicio = fim - timedelta(days=7)
    cliente = ClientePNCP()
    amostra = {}

    for codigo, nome in MODALIDADES.items():
        dados = cliente.buscar_pagina(codigo, inicio, fim)
        amostra[nome] = dados
        print(f"{nome}: {len(dados.get('data', []))} registros nesta página "
              f"(total: {dados.get('totalRegistros')})")

    pasta = Path("amostra")
    pasta.mkdir(exist_ok=True)
    (pasta / "pncp_amostra.json").write_text(
        json.dumps(amostra, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Salvo em amostra/pncp_amostra.json")


if __name__ == "__main__":
    main()