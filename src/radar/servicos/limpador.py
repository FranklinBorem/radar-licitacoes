"""Regras para arrumar os dados do PNCP antes de gravar no banco."""
import html
import re


class Limpador:
    @staticmethod
    def so_digitos(texto) -> str:
        return re.sub(r"\D", "", texto or "")

    @staticmethod
    def valor_ou_vazio(valor):
        """0,0 no PNCP quer dizer 'nao informado', entao vira vazio."""
        return valor if valor else None

    @staticmethod
    def link(texto):
        """Aproveita so links http(s) de verdade; o resto vira vazio."""
        achado = re.search(r"https?://\S+", (texto or "").strip(), re.IGNORECASE)
        return achado.group(0) if achado else None

    @staticmethod
    def texto(texto):
        """Tira HTML, espacos repetidos e prefixos como '[LICITANET] -'."""
        if not texto:
            return None
        texto = re.sub(r"<[^>]+>", " ", texto)  # remove <p>, <br> etc.
        texto = html.unescape(texto)  # &nbsp; e &amp; viram texto normal
        texto = re.sub(r"\s+", " ", texto).strip()
        return re.sub(r"^\[[^\]]+\]\s*-?\s*", "", texto) or None

    @classmethod
    def descricao_item(cls, texto):
        """Corrige o comeco repetido: 'A B A B resto' vira 'A B resto'."""
        texto = cls.texto(texto)
        if not texto:
            return None
        palavras = texto.split()
        for n in range(len(palavras) // 2, 0, -1):
            if palavras[:n] == palavras[n:2 * n]:
                return " ".join(palavras[n:])
        return texto

    @classmethod
    def cnpj_pj(cls, tipo_pessoa, numero):
        """CNPJ so se for pessoa juridica. Pessoa fisica (CPF) e descartada (LGPD)."""
        digitos = cls.so_digitos(numero)
        return digitos if tipo_pessoa == "PJ" and len(digitos) == 14 else None
