"""Configuracoes do sistema, lidas do arquivo .env ou de variaveis de ambiente."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://radar:radar@localhost:5433/radar"
    ambiente: str = "desenvolvimento"


configuracoes = Configuracoes()
