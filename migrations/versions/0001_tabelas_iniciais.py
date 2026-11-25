"""tabelas iniciais: orgao, unidade_compradora, contratacao, item_contratacao,
fornecedor, resultado_item

Revision ID: 0001
Revises:
Create Date: 2026-11-25
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE orgao (
            cnpj          CHAR(14) PRIMARY KEY,
            razao_social  TEXT NOT NULL,
            esfera        CHAR(1),
            poder         CHAR(1)
        )
    """)

    op.execute("""
        CREATE TABLE unidade_compradora (
            id              SERIAL PRIMARY KEY,
            orgao_cnpj      CHAR(14) NOT NULL REFERENCES orgao(cnpj),
            codigo_unidade  TEXT NOT NULL,
            nome            TEXT,
            municipio       TEXT,
            codigo_ibge     CHAR(7),
            uf              CHAR(2),
            UNIQUE (orgao_cnpj, codigo_unidade)
        )
    """)

    op.execute("""
        CREATE TABLE contratacao (
            id                         BIGSERIAL PRIMARY KEY,
            numero_controle_pncp       VARCHAR(30) NOT NULL UNIQUE,
            orgao_cnpj                 CHAR(14) NOT NULL REFERENCES orgao(cnpj),
            unidade_id                 INT REFERENCES unidade_compradora(id),
            ano_compra                 INT NOT NULL,
            sequencial_compra          INT NOT NULL,
            numero_compra              TEXT,
            modalidade_id              INT,
            modalidade_nome            TEXT,
            objeto                     TEXT,
            informacao_complementar    TEXT,
            situacao_id                INT,
            situacao_nome              TEXT,
            srp                        BOOLEAN,
            valor_total_estimado       NUMERIC(18,2),
            valor_total_homologado     NUMERIC(18,2),
            data_publicacao_pncp       TIMESTAMP,
            data_abertura_proposta     TIMESTAMP,
            data_encerramento_proposta TIMESTAMP,
            data_atualizacao_global    TIMESTAMP,
            link_origem                TEXT,
            dados_brutos               JSONB NOT NULL,
            coletado_em                TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX ix_contratacao_encerramento "
               "ON contratacao (data_encerramento_proposta)")
    op.execute("CREATE INDEX ix_contratacao_orgao ON contratacao (orgao_cnpj)")
    op.execute("CREATE INDEX ix_contratacao_modalidade ON contratacao (modalidade_id)")

    op.execute("""
        CREATE TABLE item_contratacao (
            id                       BIGSERIAL PRIMARY KEY,
            contratacao_id           BIGINT NOT NULL
                                     REFERENCES contratacao(id) ON DELETE CASCADE,
            numero_item              INT NOT NULL,
            descricao                TEXT,
            material_ou_servico      CHAR(1) CHECK (material_ou_servico IN ('M', 'S')),
            quantidade               NUMERIC(18,4),
            unidade_medida           TEXT,
            valor_unitario_estimado  NUMERIC(18,4),
            valor_total              NUMERIC(18,2),
            codigo_catalogo          VARCHAR(20),
            situacao_item_nome       TEXT,
            tem_resultado            BOOLEAN,
            UNIQUE (contratacao_id, numero_item)
        )
    """)
    op.execute("CREATE INDEX ix_item_catalogo ON item_contratacao (codigo_catalogo)")

    op.execute("""
        CREATE TABLE fornecedor (
            cnpj               CHAR(14) PRIMARY KEY,
            razao_social       TEXT NOT NULL,
            porte              TEXT,
            natureza_juridica  TEXT
        )
    """)

    op.execute("""
        CREATE TABLE resultado_item (
            id                         BIGSERIAL PRIMARY KEY,
            item_id                    BIGINT NOT NULL
                                       REFERENCES item_contratacao(id) ON DELETE CASCADE,
            sequencial_resultado       INT NOT NULL,
            fornecedor_cnpj            CHAR(14) REFERENCES fornecedor(cnpj),
            quantidade_homologada      NUMERIC(18,4),
            valor_unitario_homologado  NUMERIC(18,4),
            valor_total_homologado     NUMERIC(18,2),
            percentual_desconto        NUMERIC(7,4),
            ordem_classificacao        INT,
            data_resultado             DATE,
            situacao_nome              TEXT,
            UNIQUE (item_id, sequencial_resultado)
        )
    """)
    op.execute("CREATE INDEX ix_resultado_fornecedor ON resultado_item (fornecedor_cnpj)")


def downgrade() -> None:
    # ordem inversa da criação: quem depende de outra tabela sai primeiro
    op.execute("DROP TABLE resultado_item")
    op.execute("DROP TABLE fornecedor")
    op.execute("DROP TABLE item_contratacao")
    op.execute("DROP TABLE contratacao")
    op.execute("DROP TABLE unidade_compradora")
    op.execute("DROP TABLE orgao")
