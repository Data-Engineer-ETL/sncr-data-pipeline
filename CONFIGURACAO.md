# ⚙️ Guia de Configuração - Variáveis de Ambiente

## 📋 Visão Geral

Este projeto usa variáveis de ambiente para configuração, carregadas via arquivo `.env`. Todas as configurações possuem valores padrão seguros para desenvolvimento.

## 🚀 Setup Inicial

### 1. Criar Arquivo .env

```powershell
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

### 2. Editar Valores (Opcional)

```powershell
# Abrir no editor padrão
notepad .env

# Ou VS Code
code .env
```

---

## 📝 Variáveis de Ambiente Detalhadas

### 🗄️ Configurações de Banco de Dados

#### `POSTGRES_HOST`
- **Descrição**: Endereço do servidor PostgreSQL
- **Padrão**: `localhost`
- **Valores comuns**:
  - `localhost` - Desenvolvimento local
  - `postgres` - Dentro do Docker Compose
  - `db.exemplo.com` - Servidor remoto
- **Exemplo**: 
  ```env
  POSTGRES_HOST=localhost
  ```

#### `POSTGRES_PORT`
- **Descrição**: Porta do PostgreSQL
- **Padrão**: `5432`
- **Quando mudar**: Se tiver outro serviço na porta 5432
- **Exemplo**:
  ```env
  POSTGRES_PORT=5432
  ```

#### `POSTGRES_DB`
- **Descrição**: Nome do banco de dados
- **Padrão**: `sncr_db`
- **Importante**: Deve corresponder ao banco criado
- **Exemplo**:
  ```env
  POSTGRES_DB=sncr_db
  ```

#### `POSTGRES_USER`
- **Descrição**: Usuário do banco de dados
- **Padrão**: `sncr_user`
- **Importante**: Deve ter permissões de CREATE/INSERT/UPDATE
- **Exemplo**:
  ```env
  POSTGRES_USER=sncr_user
  ```

#### `POSTGRES_PASSWORD`
- **Descrição**: Senha do banco de dados
- **Padrão**: `change_me_in_production`
- **⚠️ CRÍTICO**: **SEMPRE** altere em produção!
- **Segurança**: Use senhas fortes (16+ caracteres, alfanumérico + símbolos)
- **Exemplo**:
  ```env
  # Desenvolvimento
  POSTGRES_PASSWORD=dev123456
  
  # Produção (exemplo)
  POSTGRES_PASSWORD=Xy9#mK$2pQ8@vL4n
  ```

**URL de Conexão Gerada**:
```
postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}
```

---

### 🌐 Configurações da API

#### `API_HOST`
- **Descrição**: Interface de rede que a API escuta
- **Padrão**: `0.0.0.0` (todas as interfaces)
- **Valores comuns**:
  - `0.0.0.0` - Aceita conexões de qualquer IP (produção/Docker)
  - `127.0.0.1` - Apenas localhost (desenvolvimento seguro)
- **Exemplo**:
  ```env
  API_HOST=0.0.0.0
  ```

#### `API_PORT`
- **Descrição**: Porta HTTP da API
- **Padrão**: `8000`
- **Quando mudar**: Se porta 8000 estiver ocupada
- **Exemplo**:
  ```env
  API_PORT=8000
  ```

**Acesso**: `http://localhost:{API_PORT}` (ex: http://localhost:8000)

#### `API_WORKERS`
- **Descrição**: Número de workers Uvicorn (processos paralelos)
- **Padrão**: `4`
- **Recomendações**:
  - Desenvolvimento: `1` (facilita debug)
  - Produção: `(2 × CPU cores) + 1`
  - Exemplo: CPU 4 cores → `9` workers
- **Exemplo**:
  ```env
  # Desenvolvimento
  API_WORKERS=1
  
  # Produção (4 cores)
  API_WORKERS=9
  ```

---

### 🕷️ Configurações do Scraper

#### `BASE_URL`
- **Descrição**: URL do site SNCR para extração
- **Padrão**: `https://data-engineer-challenge-production.up.railway.app`
- **Quando mudar**: Se site mudar de domínio ou testar em ambiente staging
- **Exemplo**:
  ```env
  # Produção
  BASE_URL=https://data-engineer-challenge-production.up.railway.app
  
  # Staging/Teste
  BASE_URL=https://staging.exemplo.com
  
  # Desenvolvimento local (se tiver mock)
  BASE_URL=http://localhost:3000
  ```

#### `MAX_RETRIES`
- **Descrição**: Número máximo de tentativas em caso de erro HTTP
- **Padrão**: `5`
- **Recomendações**:
  - Site estável: `3`
  - Site instável: `5-10`
  - Desenvolvimento: `2` (falha rápido)
- **Exemplo**:
  ```env
  MAX_RETRIES=5
  ```

#### `RETRY_BACKOFF_FACTOR`
- **Descrição**: Fator multiplicador para backoff exponencial
- **Padrão**: `2`
- **Como funciona**: 
  - Tentativa 1: imediato
  - Tentativa 2: 2s (2^1 × 1s)
  - Tentativa 3: 4s (2^2 × 1s)
  - Tentativa 4: 8s (2^3 × 1s)
  - Tentativa 5: 16s (2^4 × 1s)
- **Valores**:
  - Agressivo: `1.5` (retry mais rápido)
  - Padrão: `2`
  - Conservador: `3` (retry mais lento)
- **Exemplo**:
  ```env
  RETRY_BACKOFF_FACTOR=2
  ```

#### `REQUEST_TIMEOUT`
- **Descrição**: Timeout HTTP em segundos
- **Padrão**: `30`
- **Recomendações**:
  - Rede rápida: `10-20s`
  - Rede lenta: `30-60s`
  - Downloads grandes: `120s`
- **Exemplo**:
  ```env
  REQUEST_TIMEOUT=30
  ```

#### `CHECKPOINT_DIR`
- **Descrição**: Diretório para salvar checkpoints de recuperação
- **Padrão**: `./checkpoints`
- **Importante**: Deve ter permissão de escrita
- **Exemplo**:
  ```env
  CHECKPOINT_DIR=./checkpoints
  ```

---

### 🎯 Configurações de Extração

#### `TARGET_STATES`
- **Descrição**: Estados a serem extraídos (siglas UF separadas por vírgula)
- **Padrão**: `SP,MG,RJ`
- **Formato**: Siglas em maiúsculas, separadas por vírgula (sem espaços)
- **Estados válidos**: AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO
- **Exemplos**:
  ```env
  # Apenas São Paulo
  TARGET_STATES=SP
  
  # Sudeste
  TARGET_STATES=SP,MG,RJ,ES
  
  # Sul + Sudeste
  TARGET_STATES=SP,MG,RJ,ES,PR,SC,RS
  
  # Todos (exemplo com alguns)
  TARGET_STATES=SP,MG,RJ,RS,PR,SC,BA,PE,CE
  ```

---

### 📊 Configurações de Logging

#### `LOG_LEVEL`
- **Descrição**: Nível de detalhamento dos logs
- **Padrão**: `INFO`
- **Valores**:
  - `DEBUG` - Tudo (verbose, desenvolvimento)
  - `INFO` - Informações importantes (produção)
  - `WARNING` - Apenas avisos e erros
  - `ERROR` - Apenas erros
  - `CRITICAL` - Apenas erros críticos
- **Exemplo**:
  ```env
  # Desenvolvimento
  LOG_LEVEL=DEBUG
  
  # Produção
  LOG_LEVEL=INFO
  ```

---

## 🐳 Configurações para Docker

### Arquivo `.env` para Docker Compose

O Docker Compose usa as mesmas variáveis, mas com alguns ajustes:

```env
# Database (dentro do Docker)
POSTGRES_HOST=postgres  # Nome do serviço no docker-compose.yml
POSTGRES_PORT=5432
POSTGRES_DB=sncr_db
POSTGRES_USER=sncr_user
POSTGRES_PASSWORD=change_me_in_production

# API
API_HOST=0.0.0.0  # Importante: não use 127.0.0.1 no Docker!
API_PORT=8000
API_WORKERS=4

# Scraper
BASE_URL=https://data-engineer-challenge-production.up.railway.app
MAX_RETRIES=5
RETRY_BACKOFF_FACTOR=2
REQUEST_TIMEOUT=30
CHECKPOINT_DIR=/app/checkpoints  # Caminho dentro do container
LOG_LEVEL=INFO

# Extração
TARGET_STATES=SP,MG,RJ
```

---

## 🔒 Segurança e Boas Práticas

### ⚠️ NUNCA Commite o .env

```bash
# Verificar que .env está no .gitignore
cat .gitignore | grep -i ".env"

# Verificar que não foi commitado
git status
```

### 🔐 Senhas Fortes

```python
# Gerar senha segura (Python)
import secrets
import string

alphabet = string.ascii_letters + string.digits + string.punctuation
password = ''.join(secrets.choice(alphabet) for i in range(20))
print(password)
```

```powershell
# Gerar senha segura (PowerShell)
Add-Type -AssemblyName System.Web
[System.Web.Security.Membership]::GeneratePassword(20, 5)
```

### 🌐 Produção (Secrets Manager)

Em produção real, use serviços de gerenciamento de secrets:

**AWS Secrets Manager**:
```python
import boto3
import json

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='sncr/prod/db')
secrets = json.loads(response['SecretString'])

# Use secrets['POSTGRES_PASSWORD']
```

**Azure Key Vault**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)
password = client.get_secret("postgres-password").value
```

**Google Secret Manager**:
```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = "projects/PROJECT_ID/secrets/postgres-password/versions/latest"
response = client.access_secret_version(request={"name": name})
password = response.payload.data.decode("UTF-8")
```

---

## 📋 Templates para Ambientes

### Desenvolvimento Local (.env.dev)

```env
# Database - PostgreSQL local
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sncr_db_dev
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev123456

# API
API_HOST=127.0.0.1
API_PORT=8000
API_WORKERS=1

# Scraper
BASE_URL=https://data-engineer-challenge-production.up.railway.app
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2
REQUEST_TIMEOUT=30
CHECKPOINT_DIR=./checkpoints
LOG_LEVEL=DEBUG

# Extração (apenas SP para desenvolvimento)
TARGET_STATES=SP
```

### Staging (.env.staging)

```env
# Database
POSTGRES_HOST=staging-db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=sncr_staging
POSTGRES_USER=staging_user
POSTGRES_PASSWORD=STAGING_SECURE_PASSWORD_HERE

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Scraper
BASE_URL=https://staging.sncr.example.com
MAX_RETRIES=5
RETRY_BACKOFF_FACTOR=2
REQUEST_TIMEOUT=30
CHECKPOINT_DIR=/app/checkpoints
LOG_LEVEL=INFO

# Extração
TARGET_STATES=SP,MG,RJ
```

### Produção (.env.prod)

```env
# Database
POSTGRES_HOST=prod-db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=sncr_production
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=PRODUCTION_SECURE_PASSWORD_MINIMUM_20_CHARS

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=9

# Scraper
BASE_URL=https://data-engineer-challenge-production.up.railway.app
MAX_RETRIES=5
RETRY_BACKOFF_FACTOR=2
REQUEST_TIMEOUT=60
CHECKPOINT_DIR=/app/checkpoints
LOG_LEVEL=INFO

# Extração (todos os estados)
TARGET_STATES=SP,MG,RJ,ES,PR,SC,RS,BA,PE,CE,PA,AM

# Sentry para monitoramento de erros (opcional)
SENTRY_DSN=https://xxx@sentry.io/yyy
```

---

## 🧪 Validar Configuração

### Script de Validação

Crie `validate_config.py`:

```python
"""Valida configuração de variáveis de ambiente."""
import os
from pathlib import Path

required_vars = [
    'POSTGRES_HOST',
    'POSTGRES_PORT',
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'API_HOST',
    'API_PORT',
    'BASE_URL',
    'TARGET_STATES',
]

def validate():
    """Valida que todas variáveis necessárias estão definidas."""
    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    missing = []
    warnings = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        elif var == 'POSTGRES_PASSWORD' and value == 'change_me_in_production':
            warnings.append(f"⚠️ {var} está com valor padrão!")
    
    if missing:
        print(f"❌ Variáveis faltando: {', '.join(missing)}")
        return False
    
    if warnings:
        for warn in warnings:
            print(warn)
    
    print("✅ Configuração válida!")
    return True

if __name__ == "__main__":
    validate()
```

Execute:
```powershell
python validate_config.py
```

---

## 🔍 Troubleshooting

### Erro: "No .env file found"

```powershell
# Verifique se existe
Test-Path .env

# Se não, copie do exemplo
Copy-Item .env.example .env
```

### Erro: "Can't connect to database"

```powershell
# Verifique as credenciais
cat .env | grep POSTGRES

# Teste conexão manualmente
docker-compose exec postgres psql -U sncr_user -d sncr_db
```

### Variável não está sendo lida

```python
# Debug no código Python
from src.infrastructure.config import get_settings

settings = get_settings()
print(f"POSTGRES_HOST: {settings.POSTGRES_HOST}")
print(f"API_PORT: {settings.API_PORT}")
```

---

## 📚 Referências

- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [12 Factor App - Config](https://12factor.net/config)
- [OWASP - Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

## ✅ Checklist de Configuração

- [ ] Arquivo `.env` criado a partir de `.env.example`
- [ ] `POSTGRES_PASSWORD` alterado (não use `change_me_in_production`)
- [ ] `TARGET_STATES` configurado com estados desejados
- [ ] `BASE_URL` aponta para site correto
- [ ] `LOG_LEVEL` apropriado para ambiente
- [ ] `.env` está no `.gitignore` (não commite!)
- [ ] Configuração validada com `validate_config.py`
- [ ] Testes de conexão ao banco funcionando
- [ ] API responde em `http://localhost:{API_PORT}/health`

---

**Pronto! Todas as variáveis estão documentadas e prontas para uso! 🎉**
