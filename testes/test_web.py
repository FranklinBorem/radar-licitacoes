from fastapi.testclient import TestClient

from radar.web.app import app

cliente = TestClient(app)


def test_pagina_inicial_abre():
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "Radar Comercial B2G" in resposta.text


def test_rota_de_saude():
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_arquivo_css_e_servido():
    resposta = cliente.get("/static/css/estilo.css")
    assert resposta.status_code == 200
