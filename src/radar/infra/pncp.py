"""Cliente da API publica do PNCP (Portal Nacional de Contratacoes Publicas)."""
import time

import httpx

CABECALHOS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


class ErroPNCP(Exception):
    """O PNCP nao respondeu depois de varias tentativas."""


class ClientePNCP:
    CONSULTA = "https://pncp.gov.br/api/consulta/v1"
    PNCP = "https://pncp.gov.br/api/pncp/v1"

    def __init__(self, tentativas: int = 3, espera: float = 3.0):
        self.tentativas = tentativas
        self.espera = espera

    def _get(self, url: str, parametros: dict | None = None):
        """Devolve o JSON, ou None se nao ha conteudo (204/404)."""
        for tentativa in range(1, self.tentativas + 1):
            try:
                r = httpx.get(url, params=parametros, headers=CABECALHOS, timeout=60)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (204, 404):
                    return None
                if r.status_code < 500 and r.status_code != 429:
                    raise ErroPNCP(f"HTTP {r.status_code}: {r.text[:150]}")
            except httpx.HTTPError:
                pass
            time.sleep(self.espera * tentativa)  # espera mais a cada tentativa
        raise ErroPNCP(f"Sem resposta apos {self.tentativas} tentativas: {url}")

    def contratacoes(self, modalidade: int, inicio, fim, uf: str = "MG"):
        """Entrega as compras uma a uma, passando por todas as paginas."""
        pagina = 1
        while True:
            dados = self._get(f"{self.CONSULTA}/contratacoes/publicacao", {
                "dataInicial": inicio.strftime("%Y%m%d"),
                "dataFinal": fim.strftime("%Y%m%d"),
                "codigoModalidadeContratacao": modalidade,
                "uf": uf,
                "pagina": pagina,
                "tamanhoPagina": 50,
            })
            if not dados or not dados.get("data"):
                return
            yield from dados["data"]
            if pagina >= dados.get("totalPaginas", 1):
                return
            pagina += 1

    def itens(self, cnpj: str, ano: int, seq: int) -> list:
        base = f"{self.PNCP}/orgaos/{cnpj}/compras/{ano}/{seq}/itens"
        todos, pagina = [], 1
        while True:
            lote = self._get(base, {"pagina": pagina, "tamanhoPagina": 100}) or []
            todos += lote
            if len(lote) < 100:
                return todos
            pagina += 1

    def resultados(self, cnpj: str, ano: int, seq: int, numero_item: int) -> list:
        url = f"{self.PNCP}/orgaos/{cnpj}/compras/{ano}/{seq}/itens/{numero_item}/resultados"
        dados = self._get(url) or []
        return [dados] if isinstance(dados, dict) else dados
