from radar.servicos.limpador import Limpador

L = Limpador()


def test_so_digitos():
    assert L.so_digitos("04.207.000/0001-18") == "04207000000118"
    assert L.so_digitos(None) == ""


def test_valor_zero_vira_vazio():
    assert L.valor_ou_vazio(0.0) is None
    assert L.valor_ou_vazio(None) is None
    assert L.valor_ou_vazio(499.0) == 499.0


def test_link_aproveita_so_endereco_valido():
    assert L.link("https://exemplo.com.br/x") == "https://exemplo.com.br/x"
    assert L.link(": https://exemplo.com.br/x") == "https://exemplo.com.br/x"
    assert L.link("HTTPS://EXEMPLO.COM.BR/X") == "HTTPS://EXEMPLO.COM.BR/X"
    assert L.link("PROCESSO PNCP.pdf") is None
    assert L.link("      ") is None
    assert L.link(None) is None


def test_texto_tira_html_e_prefixo():
    assert L.texto("<p>SONORIZAÇÃO</p> &amp; luz") == "SONORIZAÇÃO & luz"
    assert L.texto("[LICITANET] - CONTRATAÇÃO DE EMPRESA") == "CONTRATAÇÃO DE EMPRESA"
    assert L.texto("  muitos    espaços \n aqui ") == "muitos espaços aqui"
    assert L.texto("") is None
    assert L.texto(None) is None


def test_descricao_item_corrige_comeco_repetido():
    repetida = "Cartório / Tabelionato Cartório / Tabelionato ENVIO DOCUMENTACAO"
    assert L.descricao_item(repetida) == "Cartório / Tabelionato ENVIO DOCUMENTACAO"


def test_descricao_item_normal_nao_muda():
    assert L.descricao_item("LAMPADA 12V 21/ 94604482") == "LAMPADA 12V 21/ 94604482"


def test_cnpj_so_de_pessoa_juridica():
    assert L.cnpj_pj("PJ", "04.207.000/0001-18") == "04207000000118"
    assert L.cnpj_pj("PF", "12345678901") is None  # CPF nao e guardado
    assert L.cnpj_pj("PJ", "123") is None  # tamanho invalido
    assert L.cnpj_pj(None, "04207000000118") is None
