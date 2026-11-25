"""Rotas (enderecos) do site."""
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from radar.repositorios.contratacoes import RepositorioContratacoes

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
roteador = APIRouter()
repositorio = RepositorioContratacoes()
POR_PAGINA = 20


@roteador.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@roteador.get("/saude")
def saude():
    """Usado para conferir se o sistema esta no ar."""
    return {"status": "ok"}

@roteador.get("/api/contratacoes")
def listar(texto: str | None = None, municipio: str | None = None,
           modalidade: int | None = None, abertas: bool = False, pagina: int = 1):
    pagina = max(pagina, 1)
    return repositorio.buscar(texto, municipio, modalidade, abertas,
                              POR_PAGINA, (pagina - 1) * POR_PAGINA)


@roteador.get("/api/contratacoes/detalhe")
def detalhe(numero: str):
    # o número do PNCP tem "/", então vai como parâmetro e não no caminho
    compra = repositorio.obter(numero)
    if compra is None:
        raise HTTPException(status_code=404, detail="Compra não encontrada")
    return compra