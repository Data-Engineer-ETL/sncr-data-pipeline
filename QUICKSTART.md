# Guia de Início Rápido - SNCR Pipeline

## ⚡ TL;DR

```bash
# Clone, configure e execute em 3 comandos
git clone <repo-url> && cd challange
cp .env.example .env
docker-compose up -d

# API estará em http://localhost:8000
```

## 📋 Checklist de Instalação

### Pré-requisitos

- [ ] Docker 20.10+ instalado
- [ ] Docker Compose 2.0+ instalado
- [ ] 2GB+ RAM disponível
- [ ] 5GB+ espaço em disco

### Verificação

```powershell
# Windows PowerShell
docker --version          # Deve mostrar 20.10+
docker-compose --version  # Deve mostrar 2.0+
```

## 🚀 Início Rápido

### Passo 1: Clone e Configure

```powershell
# Clone o repositório
git clone <repo-url>
cd challange

# Copie o arquivo de configuração
cp .env.example .env

# (Opcional) Edite .env para customizar
# Por padrão, extrai dados de SP, MG e RJ
```

### Passo 2: Inicie os Serviços

```powershell
# Inicia PostgreSQL e API
docker-compose up -d

# Acompanhe os logs
docker-compose logs -f api
```

Aguarde aparecer:
```
INFO:     Started server process
INFO:     Application startup complete
```

### Passo 3: Verifique

```powershell
# Health check
curl http://localhost:8000/health

# Deve retornar:
# {"status":"healthy","timestamp":"...","database":"connected"}
```

## 📊 Executando o ETL

### Primeira Extração

```powershell
# Extrai dados dos estados configurados (SP, MG, RJ por padrão)
docker-compose --profile etl up etl

# Acompanhe o progresso
docker-compose logs -f etl
```

**Tempo esperado**: ~5-15 minutos (depende da quantidade de municípios)

### Verificar Dados

```powershell
# Estatísticas
curl http://localhost:8000/stats

# Exemplo de resposta:
# {
#   "total_imoveis": 1520,
#   "total_pessoas": 1843,
#   "total_vinculos": 2015,
#   "total_estados": 3,
#   "total_municipios": 15
# }
```

## 🔍 Consultando a API

### Endpoints Disponíveis

```powershell
# Página inicial
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Estatísticas
curl http://localhost:8000/stats

# Buscar imóvel (substitua pelo código real)
curl http://localhost:8000/imovel/12345678901234567
```

### Exemplo de Consulta

```powershell
# Buscar imóvel
$codigo = "12345678901234567"
curl "http://localhost:8000/imovel/$codigo"
```

**Resposta esperada**:
```json
{
  "codigo_incra": "12345678901234567",
  "area_ha": 142.5,
  "situacao": "Ativo",
  "proprietarios": [
    {
      "nome_completo": "Maria Silva",
      "cpf": "***.***.*72-45",
      "vinculo": "Proprietário",
      "participacao_pct": 100.0
    }
  ]
}
```

## 🛠️ Comandos Úteis

### Docker Compose

```powershell
# Ver logs
docker-compose logs -f [serviço]

# Parar serviços
docker-compose down

# Reiniciar
docker-compose restart

# Status dos containers
docker-compose ps

# Reconstruir imagens
docker-compose build
```

### Banco de Dados

```powershell
# Conectar ao PostgreSQL
docker-compose exec postgres psql -U sncr_user -d sncr_db

# Queries úteis:
# SELECT COUNT(*) FROM imoveis;
# SELECT * FROM imoveis LIMIT 10;
# \dt  -- lista tabelas
# \d+ imoveis  -- descreve tabela
```

### Checkpoints

```powershell
# Ver progresso de extração
cat checkpoints/SP_checkpoint.json

# Limpar checkpoint (para reprocessar)
rm checkpoints/SP_checkpoint.json
docker-compose --profile etl up etl
```

## 🐛 Troubleshooting

### Porta 8000 já em uso

```powershell
# Mude a porta no .env
echo "API_PORT=8001" >> .env
docker-compose up -d
```

### PostgreSQL não inicia

```powershell
# Veja os logs
docker-compose logs postgres

# Recreie o container
docker-compose down -v
docker-compose up -d postgres
```

### API retorna 500

```powershell
# Verifique se PostgreSQL está saudável
docker-compose ps

# Veja logs da API
docker-compose logs api

# Teste conexão com banco
docker-compose exec api python -c "from src.infrastructure.database import db; import asyncio; asyncio.run(db.connect())"
```

### ETL falha

```powershell
# Veja logs detalhados
docker-compose --profile etl logs etl

# Limpe checkpoints e tente novamente
rm -r checkpoints/*
docker-compose --profile etl up etl
```

## 📚 Próximos Passos

### 1. Explore a API

- [ ] Abra http://localhost:8000/docs (Swagger UI)
- [ ] Teste endpoints interativamente
- [ ] Use Redoc em http://localhost:8000/redoc

### 2. Customize Extração

Edite `.env`:
```env
# Adicione mais estados
TARGET_STATES=SP,MG,RJ,PR,SC

# Ajuste retry
MAX_RETRIES=10
RETRY_BACKOFF_FACTOR=3
```

Reexecute:
```powershell
docker-compose --profile etl up etl
```

### 3. Desenvolva Localmente

```powershell
# Crie ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Execute API em modo dev
python -m uvicorn src.interfaces.api:app --reload
```

### 4. Execute Testes

```powershell
# Com Docker
docker-compose exec api pytest tests/ -v

# Local
pytest tests/ -v --cov=src
```

## 🎓 Aprendendo Mais

- **Arquitetura**: Leia [ARCHITECTURE.md](ARCHITECTURE.md)
- **Índices**: Veja [migrations/INDICES.md](migrations/INDICES.md)
- **Documentação**: README.md completo

## 💡 Dicas

### Performance

```powershell
# Veja queries lentas no PostgreSQL
docker-compose exec postgres psql -U sncr_user -d sncr_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### Logs

```powershell
# Logs estruturados em JSON
docker-compose exec api cat logs/sncr_$(date +%Y-%m-%d).log | jq
```

### Backup

```powershell
# Backup do banco
docker-compose exec postgres pg_dump -U sncr_user sncr_db > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U sncr_user sncr_db < backup_20260330.sql
```

## 🆘 Precisa de Ajuda?

1. **Erros**: Veja logs com `docker-compose logs -f`
2. **Problemas conhecidos**: Veja seção Troubleshooting no README
3. **Arquitetura**: Leia ARCHITECTURE.md
4. **Código**: Todos os arquivos têm docstrings detalhadas

---

**Divirta-se explorando o SNCR Pipeline! 🚀**
