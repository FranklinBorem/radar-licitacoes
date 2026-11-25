# Radar Comercial B2G

Plataforma de inteligencia comercial com dados publicos de compras e licitacoes do setor publico.
Ajuda empresas a descobrir quem compra o que elas vendem, onde, quanto e com que frequencia.

> Projeto em desenvolvimento. Nome de trabalho.

## Tecnologias

Python 3.12, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Jinja2, HTML, CSS e JavaScript.

## Como rodar no seu computador

### 1. Criar o ambiente virtual e instalar as dependencias

Linux/Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 2. Criar o arquivo de configuracao

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

### 3. Subir o banco de dados

```bash
docker compose up -d
```

### 4. Rodar o site

```bash
uvicorn radar.web.app:app --reload
```

Abra http://127.0.0.1:8000 no navegador.

### 5. Rodar os testes

```bash
pytest
ruff check .
```

## Estrutura do projeto

```
src/radar/
  dominio/        objetos do negocio (Python puro)
  servicos/       casos de uso
  repositorios/   acesso ao banco
  infra/          PNCP, e-mail, conexao com o banco
  web/            rotas, templates HTML, CSS e JS
  analise/        consultas e relatorios de dados
migrations/       mudancas nas tabelas (Alembic)
notebooks/        analises exploratorias
testes/           testes automaticos
```

## Fonte dos dados

Portal Nacional de Contratacoes Publicas (PNCP): https://pncp.gov.br
Projeto independente, sem vinculo com o governo.
