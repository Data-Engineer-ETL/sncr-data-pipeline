# Arquitetura do Sistema SNCR

## Visão Geral

Este documento descreve a arquitetura detalhada do pipeline de dados SNCR, suas decisões de design e padrões utilizados.

## Princípios de Design

### 1. Clean Architecture

O sistema segue os princípios da Clean Architecture (Uncle Bob), com separação clara entre:

- **Domain Layer**: Regras de negócio puras, independentes de frameworks
- **Infrastructure Layer**: Configuração, logging, database connections
- **Adapters Layer**: Comunicação com sistemas externos (web, database)
- **Interfaces Layer**: Pontos de entrada (API REST)

```
┌─────────────────────────────────────────┐
│          Interfaces (API)               │
│  ┌───────────────────────────────────┐  │
│  │        Adapters                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │    Infrastructure           │  │  │
│  │  │  ┌───────────────────────┐  │  │  │
│  │  │  │      Domain           │  │  │  │
│  │  │  │  (Business Logic)    │  │  │  │
│  │  │  └───────────────────────┘  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### 2. Dependency Rule

Dependências apontam sempre para dentro:
- Domain não depende de nada
- Infrastructure depende de Domain
- Adapters dependem de Domain e Infrastructure
- Interfaces dependem de tudo

### 3. SOLID Principles

- **S**ingle Responsibility: Cada classe tem uma única razão para mudar
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Abstrações bem definidas
- **I**nterface Segregation: Interfaces específicas
- **D**ependency Inversion: Dependa de abstrações, não de concretizações

## Componentes

### Domain Layer (`src/domain/`)

#### models.py

Define entidades core do sistema usando Pydantic:

```python
- Imovel: Propriedade rural
- Pessoa: Proprietário/Arrendatário
- VinculoPessoa: Relacionamento
- ExtractionMetadata: Metadados de extração
```

**Responsabilidades**:
- Validação de dados (CPF, código INCRA, área)
- Regras de negócio (anonimização de CPF)
- Sem dependências externas

### Infrastructure Layer (`src/infrastructure/`)

#### config.py

Gerenciamento centralizado de configuração usando Pydantic Settings:

```python
class Settings(BaseSettings):
    - Carrega de .env
    - Validação de tipos
    - Valores default
    - Properties derivadas (database_url)
```

#### database.py

Connection pooling com asyncpg:

```python
class Database:
    - Pool de conexões (min=2, max=10)
    - Context managers para acquire/transaction
    - Lifecycle management (connect/disconnect)
```

**Por que asyncpg?**
- 3-5x mais rápido que psycopg2
- Suporte nativo a async/await
- Connection pooling eficiente

#### logging.py

Logging estruturado com Loguru:

```python
- Console: formato colorido para dev
- File: JSON estruturado para produção
- Rotação diária com compressão
- Retenção de 30 dias
```

#### checkpoint.py

Gerenciamento de checkpoints para recovery:

```python
class CheckpointManager:
    - Salva progresso por estado
    - Permite retomada após falha
    - Formato JSON simples
    - Thread-safe
```

### Adapters Layer (`src/adapters/`)

#### scraper.py

Web scraping robusto:

```python
class SNCRScraper:
    - Retry com backoff exponencial
    - Detecção de anti-bot
    - Session management
    - Rate limiting (1s entre requests)
    - CSV parsing com pandas
```

**Estratégia de Retry**:
- 5 tentativas máximo
- Backoff: 2^n segundos (1, 2, 4, 8, 16)
- Retry em: HTTPError, TimeoutException
- Detecta: bot challenges, Cloudflare

#### repository.py

Operações de banco idempotentes:

```python
class ImovelRepository:
    - Upsert (INSERT ... ON CONFLICT)
    - Transactions atômicas
    - Bulk operations
    - Query builders
```

**Padrão Upsert**:
```sql
INSERT INTO tabela (campos...)
VALUES (valores...)
ON CONFLICT (chave_natural)
DO UPDATE SET campos = EXCLUDED.campos
RETURNING id
```

### Interfaces Layer (`src/interfaces/`)

#### api.py

API REST com FastAPI:

```python
- Lifespan management (startup/shutdown)
- Exception handlers globais
- Health checks
- OpenAPI docs automático
```

**Endpoints**:
- `GET /`: Info da API
- `GET /health`: Health check
- `GET /stats`: Estatísticas
- `GET /imovel/{codigo}`: Consulta principal

#### schemas.py

Response models com Pydantic:

```python
- ImovelResponse
- ProprietarioResponse
- ErrorResponse
- Exemplos para documentação
```

## Fluxos de Dados

### 1. ETL Flow

```
[Web] → [Scraper] → [DataFrame] → [Transform] → [Repository] → [PostgreSQL]
   ↓         ↓            ↓             ↓             ↓
[Retry]  [Session]   [Validate]   [Models]    [Upsert]
```

**Passos**:
1. Scraper faz HTTP GET/POST para site SNCR
2. Retry automático em falhas (exponential backoff)
3. Parse CSV para pandas DataFrame
4. Transform: DataFrame → Domain Models (validação)
5. Repository faz upsert no PostgreSQL
6. Transaction commit ou rollback
7. Checkpoint salvo

### 2. API Query Flow

```
[HTTP Request] → [FastAPI] → [Repository] → [PostgreSQL]
                     ↓             ↓              ↓
                [Validate]    [Query]       [Index Scan]
                     ↓             ↓              ↓
                [Response] ← [Transform] ← [Row Data]
```

**Passos**:
1. Request chega em `/imovel/{codigo}`
2. FastAPI valida formato (17 dígitos)
3. Repository executa query otimizada
4. PostgreSQL usa índice (< 10ms)
5. Transform: dict → Response Model
6. Anonimiza CPF
7. JSON Response

## Decisões Técnicas

### 1. Por que PostgreSQL?

✅ ACID compliance  
✅ Índices avançados (B-Tree, GiST)  
✅ Views materializadas  
✅ JSON support  
✅ Replication e HA  

### 2. Por que FastAPI?

✅ Performance (Starlette + Pydantic)  
✅ OpenAPI automático  
✅ Async nativo  
✅ Type hints e validação  
✅ Dependency injection  

### 3. Por que não usar ORM completo?

ORMs (SQLAlchemy Core) adicionam overhead e abstrações desnecessárias para este caso de uso:

- ✅ SQL explícito é mais performático
- ✅ Controle fino sobre queries
- ✅ Upserts complexos são mais claros
- ✅ Menos "magic", mais previsível

### 4. Modelagem Normalizada vs Desnormalizada?

**Escolha**: Normalizada (3NF)

**Razão**:
- ✅ Sem duplicação de dados (CPF, nome)
- ✅ Consistência referencial
- ✅ Fácil atualização
- ✅ View desnormalizada para queries

**Trade-off**: JOINs, mas índices compensam

### 5. Async vs Sync?

**Escolha**: Async (asyncio, asyncpg, FastAPI)

**Razão**:
- ✅ Escalabilidade: 1000s de conexões concorrentes
- ✅ Eficiência: não bloqueia em I/O
- ✅ API moderna: async/await nativo

**Trade-off**: Complexidade, mas Python 3.11+ melhora muito

## Padrões Utilizados

### 1. Repository Pattern

Abstrai acesso a dados:
```python
repository.get_imovel_by_codigo(codigo)  # Interface limpa
# vs
await conn.fetch("SELECT ... JOIN ...")  # SQL direto
```

### 2. Dependency Injection
 
FastAPI injeta dependências:
```python
async def endpoint(db: Database = Depends(get_db)):
    ...
```

### 3. Factory Pattern

CheckpointManager, ImovelRepository criam instâncias:
```python
manager = CheckpointManager(checkpoint_dir)
```

### 4. Strategy Pattern

Retry strategies configuráveis:
```python
@retry(stop=stop_after_attempt(5), wait=wait_exponential(...))
```

## Segurança

### 1. Anonimização de CPF

```python
"12345678972" → "***.***.*72-72"
```

Apenas últimos 2 dígitos + verificador expostos.

### 2. SQL Injection Protection

asyncpg usa prepared statements:
```python
await conn.fetch("SELECT * WHERE codigo = $1", codigo)  # Safe
```

### 3. Input Validation

Pydantic valida todos os inputs:
```python
class Imovel(BaseModel):
    codigo_incra: str
    
    @field_validator("codigo_incra")
    def validate(cls, v):
        if len(v) != 17:
            raise ValueError(...)
```

### 4. Secrets Management

`.env` não commitado, use secrets manager em produção:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets

## Performance

### 1. Índices

8 índices estratégicos:
- B-Tree para lookups (O(log n))
- Compostos para queries multi-coluna
- Unique para constraints

### 2. Connection Pooling

Pool de 2-10 conexões:
- Evita overhead de connect/disconnect
- Reusa conexões
- Timeout de 60s

### 3. Bulk Operations

Inserção em lote:
```python
async with conn.transaction():
    for batch in chunks(imoveis, 100):
        await insert_batch(batch)
```

### 4. Async I/O

Não bloqueia em I/O:
- HTTP requests paralelos
- DB queries concorrentes
- 1000+ req/s possível

## Observabilidade

### 1. Logging

Estruturado em JSON:
```json
{"timestamp": "...", "level": "INFO", "message": "...", "extra": {...}}
```

### 2. Métricas (Futuro)

Prometheus:
- request_duration_seconds
- db_query_duration_seconds
- extraction_success_total

### 3. Tracing (Futuro)

OpenTelemetry:
- Request → API → DB → Response
- Distributed tracing

## Testabilidade

### 1. Separation of Concerns

Cada camada testável independentemente:
- Domain: unit tests puros
- Repository: integration tests com DB de teste
- API: API tests com TestClient

### 2. Dependency Injection

Fácil mockar dependências:
```python
def test_endpoint(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    ...
```

### 3. Fixtures

pytest fixtures para setup/teardown:
```python
@pytest.fixture
async def db_connection():
    conn = await asyncpg.connect(...)
    yield conn
    await conn.close()
```

## Escalabilidade

### Horizontal Scaling

- ✅ API: stateless, pode replicar
- ✅ ETL: pode particionar por estado
- ✅ DB: read replicas PostgreSQL

### Vertical Scaling

- ✅ Connection pool ajustável
- ✅ Worker processes configurável
- ✅ Batch size tunável

### Caching (Futuro)

- ✅ Redis para queries frequentes
- ✅ TTL configurável
- ✅ Cache warming

## Deployment

### Docker

Multi-stage build:
- Builder: instala deps
- Runtime: apenas necessário
- Imagem final: ~200MB

### Docker Compose

Orquestração local:
- postgres + api + etl
- Health checks
- Volume persistence
- Network isolation

### Kubernetes (Futuro)

- Deployments para API/ETL
- StatefulSet para PostgreSQL
- HPA para autoscaling
- Ingress para roteamento

## Manutenção

### Migrations

Schema versionado:
- `migrations/001_initial.sql`
- `migrations/002_add_indexes.sql`
- Ferramenta: Alembic (futuro)

### Backups

PostgreSQL:
- wal-g para backups contínuos
- Point-in-time recovery
- Retenção configurável

### Monitoring

- Health checks em `/health`
- Logs estruturados
- Alertas em falhas

---

**Revisado em**: 2026-03-30  
**Versão**: 1.0.0
