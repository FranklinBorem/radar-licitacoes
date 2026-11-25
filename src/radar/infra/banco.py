"""Conexao com o PostgreSQL."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from radar.config import configuracoes


class Base(DeclarativeBase):
    """Classe base de todas as tabelas."""


engine = create_engine(configuracoes.database_url, pool_pre_ping=True)
SessaoLocal = sessionmaker(bind=engine, expire_on_commit=False)
