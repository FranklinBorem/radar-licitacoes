"""Criacao da aplicacao web."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from radar.web.rotas import roteador

PASTA_WEB = Path(__file__).parent


def criar_app() -> FastAPI:
    app = FastAPI(title="Radar Comercial B2G")
    app.mount("/static", StaticFiles(directory=PASTA_WEB / "static"), name="static")
    app.include_router(roteador)
    return app


app = criar_app()
