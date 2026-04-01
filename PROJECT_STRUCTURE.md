# Estrutura do Projeto SNCR

```
challange/
│
├── src/                                 # Código-fonte principal
│   ├── __init__.py
│   │
│   ├── domain/                         # 🎯 Camada de Domínio (Regras de Negócio)
│   │   ├── __init__.py
│   │   └── models.py                   # Entidades: Imovel, Pessoa, VinculoPessoa
│   │
│   ├── infrastructure/                 # ⚙️ Camada de Infraestrutura
│   │   ├── __init__.py
│   │   ├── config.py                   # Settings com Pydantic
│   │   ├── database.py                 # Connection pooling (asyncpg)
│   │   ├── logging.py                  # Logging estruturado (Loguru)
│   │   └── checkpoint.py               # Gerenciamento de checkpoints
│   │
│   ├── adapters/                       # 🔌 Adaptadores Externos
│   │   ├── __init__.py
│   │   ├── scraper.py                  # Web scraping com retry
│   │   └── repository.py               # Operações de banco (idempotentes)
│   │
│   └── interfaces/                     # 🌐 Interfaces Externas
│       ├── __init__.py
│       ├── api.py                      # FastAPI application
│       └── schemas.py                  # Response models (Pydantic)
│
├── scripts/                            # 📜 Scripts utilitários
│   ├── __init__.py
│   ├── run_etl.py                     # Pipeline ETL completo
│   ├── init_db.py                     # Inicialização do banco
│   └── seed_db.py                      # Dados de seed para testes
│
├── migrations/                         # 🗄️ Migrações de Banco
│   ├── schema.sql                      # Schema PostgreSQL completo
│   └── INDICES.md                      # Documentação de índices
│
├── tests/                              # 🧪 Testes
│   ├── __init__.py
│   ├── conftest.py                     # Fixtures pytest
│   └── test_models.py                  # Testes unitários
│
├── logs/                               # 📊 Logs da aplicação
│   └── sncr_YYYY-MM-DD.log            # Logs JSON estruturados
│
├── checkpoints/                        # 💾 Checkpoints de extração
│   └── {UF}_checkpoint.json           # Progresso por estado
│
├── data/                               # 📁 Dados intermediários
│   └── *.csv                          # CSVs baixados (temporário)
│
├── .env.example                        # 🔐 Template de variáveis de ambiente
├── .env                               # 🔐 Variáveis reais (gitignored)
├── .gitignore                         # Git ignore rules
├── .dockerignore                      # Docker ignore rules
│
├── requirements.txt                    # 📦 Dependências Python
├── pyproject.toml                     # ⚙️ Configuração de ferramentas
│
├── Dockerfile                         # 🐳 Imagem Docker (multi-stage)
├── docker-compose.yml                 # 🐳 Orquestração (postgres + api + etl)
├── Makefile                           # 🛠️ Comandos auxiliares
│
├── README.md                          # 📖 Documentação principal
├── ARCHITECTURE.md                    # 🏗️ Decisões técnicas detalhadas
├── QUICKSTART.md                      # 🚀 Guia de início rápido
├── CHANGELOG.md                       # 📝 Histórico de mudanças
└── CONTRIBUTING.md                    # 🤝 Guia de contribuição
```

## 📊 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SNCR Data Pipeline                            │
└─────────────────────────────────────────────────────────────────────────┘

1. EXTRAÇÃO (ETL)
   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
   │  SNCR    │────▶│ Scraper  │────▶│DataFrame │────▶│Transform │
   │  Site    │     │ (retry)  │     │ (pandas) │     │(Pydantic)│
   └──────────┘     └──────────┘     └──────────┘     └──────────┘
                          │                                  │
                          ▼                                  ▼
                    ┌──────────┐                      ┌──────────┐
                    │Checkpoint│                      │Repository│
                    │  Manager │                      │ (upsert) │
                    └──────────┘                      └──────────┘
                                                            │
                                                            ▼
                                                      ┌──────────┐
                                                      │PostgreSQL│
                                                      │  (8 idx) │
                                                      └──────────┘

2. CONSULTA (API)
   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
   │  HTTP    │────▶│ FastAPI  │────▶│Repository│────▶│PostgreSQL│
   │ Request  │     │ Validate │     │  Query   │     │Index Scan│
   └──────────┘     └──────────┘     └──────────┘     └──────────┘
                          │                                  │
                          │                                  ▼
                          │                            ┌──────────┐
                          │                            │  Result  │
                          │                            │   Row    │
                          │                            └──────────┘
                          │                                  │
                          ▼                                  ▼
                    ┌──────────┐                      ┌──────────┐
                    │Anonymize │◀─────────────────────│Transform │
                    │   CPF    │                      │  to JSON │
                    └──────────┘                      └──────────┘
                          │
                          ▼
                    ┌──────────┐
                    │  JSON    │
                    │ Response │
                    └──────────┘
```

## 🗂️ Camadas e Responsabilidades

### Domain Layer (Verde)
```
┌─────────────────────────────────────┐
│          DOMAIN MODELS              │
├─────────────────────────────────────┤
│ • Imovel                            │
│ • Pessoa                            │
│ • VinculoPessoa                     │
│ • ExtractionMetadata                │
│                                     │
│ Responsabilidades:                  │
│ ✓ Validação de dados                │
│ ✓ Regras de negócio                 │
│ ✓ Anonimização de CPF               │
│ ✗ NÃO conhece banco ou HTTP         │
└─────────────────────────────────────┘
```

### Infrastructure Layer (Azul)
```
┌─────────────────────────────────────┐
│        INFRASTRUCTURE               │
├─────────────────────────────────────┤
│ • Config (Settings)                 │
│ • Database (Connection Pool)        │
│ • Logging (Structured)              │
│ • Checkpoint (Recovery)             │
│                                     │
│ Responsabilidades:                  │
│ ✓ Configuração centralizada         │
│ ✓ Conexões e recursos               │
│ ✓ Observabilidade                   │
│ ✗ NÃO contém lógica de negócio      │
└─────────────────────────────────────┘
```

### Adapters Layer (Amarelo)
```
┌─────────────────────────────────────┐
│           ADAPTERS                  │
├─────────────────────────────────────┤
│ • Scraper (Web → DataFrame)         │
│ • Repository (Model → Database)     │
│                                     │
│ Responsabilidades:                  │
│ ✓ Comunicação externa               │
│ ✓ Tradução de formatos              │
│ ✓ Retry e resilience                │
│ ✗ NÃO define modelos                │
└─────────────────────────────────────┘
```

### Interfaces Layer (Vermelho)
```
┌─────────────────────────────────────┐
│          INTERFACES                 │
├─────────────────────────────────────┤
│ • API (FastAPI)                     │
│ • Schemas (Response Models)         │
│                                     │
│ Responsabilidades:                  │
│ ✓ Endpoints HTTP                    │
│ ✓ Serialization                     │
│ ✓ Documentation (OpenAPI)           │
│ ✗ NÃO contém lógica complexa        │
└─────────────────────────────────────┘
```

## 🔄 Fluxo de Dependências

```
  Interfaces Layer
        ▲
        │ depende de
        │
   Adapters Layer
        ▲
        │ depende de
        │
Infrastructure Layer
        ▲
        │ depende de
        │
    Domain Layer
   (sem dependências)
```

**Regra de Ouro**: Dependências apontam sempre PARA DENTRO
- Domain é o núcleo, independente de tudo
- Infrastructure depende apenas de Domain
- Adapters podem usar Domain e Infrastructure
- Interfaces usa tudo, mas não é usado por ninguém

## 📦 Módulos Principais

| Módulo | Linhas | Complexidade | Descrição |
|--------|--------|--------------|-----------|
| `models.py` | ~200 | Baixa | Entidades Pydantic |
| `scraper.py` | ~350 | Alta | Web scraping com retry |
| `repository.py` | ~400 | Média | Operações de banco |
| `api.py` | ~250 | Baixa | Endpoints FastAPI |
| `run_etl.py` | ~200 | Média | Orquestração ETL |
| `schema.sql` | ~300 | Baixa | DDL PostgreSQL |

**Total**: ~1700 linhas de código Python + 300 linhas SQL

## 🔍 Pontos de Entrada

### Produção
```bash
# API REST
docker-compose up -d api
→ http://localhost:8000

# ETL Pipeline
docker-compose --profile etl up etl
→ Executa extração completa
```

### Desenvolvimento
```bash
# API em modo dev
python -m uvicorn src.interfaces.api:app --reload

# ETL standalone
python scripts/run_etl.py

# Seed database
python scripts/seed_db.py
```

### Testes
```bash
# Unit tests
pytest tests/test_models.py -v

# Integration tests (futuro)
pytest tests/integration/ -v
```

## 🎯 Arquivos Chave

| Arquivo | Função | Criticidade |
|---------|--------|-------------|
| `src/domain/models.py` | Validação core | ⭐⭐⭐⭐⭐ |
| `src/adapters/repository.py` | Persistência | ⭐⭐⭐⭐⭐ |
| `src/interfaces/api.py` | Endpoints | ⭐⭐⭐⭐ |
| `migrations/schema.sql` | Schema | ⭐⭐⭐⭐⭐ |
| `docker-compose.yml` | Orquestração | ⭐⭐⭐⭐ |
| `.env` | Configuração | ⭐⭐⭐⭐⭐ |

## 📈 Métricas do Projeto

```
Estatísticas (até 2026-03-30):
├── Arquivos Python: 18
├── Arquivos SQL: 1
├── Arquivos Docker: 2
├── Arquivos Docs: 7
├── Total de Linhas: ~3500
└── Cobertura de Testes: ~30% (básico)

Complexidade:
├── Domain: ●●○○○ (Simples)
├── Infrastructure: ●●○○○ (Simples)
├── Adapters: ●●●●○ (Complexo)
├── Interfaces: ●●○○○ (Simples)
└── Geral: ●●●○○ (Médio)
```

---

**Legenda de Símbolos**:
- 📦 Dependências/Pacotes
- 🔐 Segurança/Configuração
- 🐳 Docker/Containers
- 📖 Documentação
- 🧪 Testes
- 📜 Scripts
- 🗄️ Banco de Dados
- ⚙️ Configuração
- 🔌 Integrações
- 🌐 API/Web
