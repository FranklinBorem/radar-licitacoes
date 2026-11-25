"""Rotas (enderecos) do site."""
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
roteador = APIRouter()


@roteador.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@roteador.get("/saude")
def saude():
    """Usado para conferir se o sistema esta no ar."""
    return {"status": "ok"}
