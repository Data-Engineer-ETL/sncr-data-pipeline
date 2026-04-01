# Exemplos de Uso da API SNCR

Este arquivo contém exemplos práticos de como usar a API em diferentes cenários.

## 🚀 Setup Inicial

### 1. Inicie os serviços

```powershell
# Windows PowerShell
docker-compose up -d
```

### 2. Aguarde a API ficar pronta

```powershell
# Verifique health
curl http://localhost:8000/health
```

### 3. (Opcional) Popule com dados de exemplo

```powershell
docker-compose exec api python scripts/seed_db.py
```

---

## 📡 Endpoints Disponíveis

### Root - Informações da API

**Request**:
```powershell
curl http://localhost:8000/
```

**Response**:
```json
{
  "name": "SNCR API",
  "version": "1.0.0",
  "description": "Sistema Nacional de Cadastro Rural - API de Consulta",
  "endpoints": {
    "health": "/health",
    "stats": "/stats",
    "imovel": "/imovel/{codigo_incra}",
    "docs": "/docs"
  }
}
```

---

### Health Check

**Request**:
```powershell
curl http://localhost:8000/health
```

**Response (Healthy)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-30T10:30:00.123456Z",
  "database": "connected"
}
```

**Response (Unhealthy)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2026-03-30T10:30:00.123456Z",
  "database": "disconnected"
}
```

---

### Estatísticas do Banco

**Request**:
```powershell
curl http://localhost:8000/stats
```

**Response**:
```json
{
  "total_imoveis": 15420,
  "total_pessoas": 18350,
  "total_vinculos": 20100,
  "total_estados": 3,
  "total_municipios": 45
}
```

---

### Buscar Imóvel por Código INCRA

#### Caso 1: Imóvel Encontrado

**Request**:
```powershell
curl http://localhost:8000/imovel/12345678901234567
```

**Response** (Status 200):
```json
{
  "codigo_incra": "12345678901234567",
  "area_ha": 142.5,
  "situacao": "Ativo",
  "proprietarios": [
    {
      "nome_completo": "Maria Aparecida de Souza",
      "cpf": "***.***.*72-45",
      "vinculo": "Proprietário",
      "participacao_pct": 100.0
    }
  ]
}
```

#### Caso 2: Múltiplos Proprietários

**Request**:
```powershell
curl http://localhost:8000/imovel/98765432109876543
```

**Response** (Status 200):
```json
{
  "codigo_incra": "98765432109876543",
  "area_ha": 85.75,
  "situacao": "Ativo",
  "proprietarios": [
    {
      "nome_completo": "Ana Paula Costa",
      "cpf": "***.***.*44-44",
      "vinculo": "Proprietário",
      "participacao_pct": 40.0
    },
    {
      "nome_completo": "João Pedro Silva",
      "cpf": "***.***.*09-09",
      "vinculo": "Proprietário",
      "participacao_pct": 60.0
    }
  ]
}
```

#### Caso 3: Proprietário + Arrendatário

**Request**:
```powershell
curl http://localhost:8000/imovel/11223344556677889
```

**Response** (Status 200):
```json
{
  "codigo_incra": "11223344556677889",
  "area_ha": 450.25,
  "situacao": "Ativo",
  "proprietarios": [
    {
      "nome_completo": "Roberto Santos Alves",
      "cpf": "***.***.*99-99",
      "vinculo": "Arrendatário",
      "participacao_pct": 20.0
    },
    {
      "nome_completo": "Fernanda Rodrigues Lima",
      "cpf": "***.***.*56-56",
      "vinculo": "Proprietário",
      "participacao_pct": 80.0
    }
  ]
}
```

#### Caso 4: Imóvel Não Encontrado

**Request**:
```powershell
curl http://localhost:8000/imovel/99999999999999999
```

**Response** (Status 404):
```json
{
  "detail": "Imóvel não encontrado para o código INCRA fornecido"
}
```

#### Caso 5: Código Inválido

**Request**:
```powershell
curl http://localhost:8000/imovel/123
```

**Response** (Status 422):
```json
{
  "detail": "Código INCRA deve ter exatamente 17 dígitos"
}
```

---

## 🧪 Testando com PowerShell

### Script Completo de Testes

```powershell
# teste_api.ps1
$BASE_URL = "http://localhost:8000"

Write-Host "=== Testando API SNCR ===" -ForegroundColor Green

# 1. Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
$response | ConvertTo-Json -Depth 10

# 2. Estatísticas
Write-Host "`n2. Estatísticas..." -ForegroundColor Yellow
$stats = Invoke-RestMethod -Uri "$BASE_URL/stats" -Method Get
$stats | ConvertTo-Json -Depth 10

# 3. Buscar Imóveis
Write-Host "`n3. Buscando imóveis..." -ForegroundColor Yellow

$codigos = @(
    "12345678901234567",
    "98765432109876543",
    "11223344556677889"
)

foreach ($codigo in $codigos) {
    Write-Host "`nBuscando código: $codigo" -ForegroundColor Cyan
    
    try {
        $imovel = Invoke-RestMethod -Uri "$BASE_URL/imovel/$codigo" -Method Get
        Write-Host "✓ Encontrado: $($imovel.municipio)/$($imovel.uf)" -ForegroundColor Green
        Write-Host "  Área: $($imovel.area_ha) ha" -ForegroundColor Gray
        Write-Host "  Proprietários: $($imovel.proprietarios.Count)" -ForegroundColor Gray
        
        foreach ($prop in $imovel.proprietarios) {
            Write-Host "    - $($prop.nome_completo) ($($prop.cpf))" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "✗ Não encontrado" -ForegroundColor Red
    }
}

# 4. Testar código inválido
Write-Host "`n4. Testando código inválido..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/imovel/123" -Method Get -ErrorAction Stop
}
catch {
    $errorMessage = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "✓ Erro esperado: $($errorMessage.detail)" -ForegroundColor Green
}

Write-Host "`n=== Testes Concluídos ===" -ForegroundColor Green
```

**Executar**:
```powershell
.\teste_api.ps1
```

---

## 🔧 Testando com curl (Alternativo)

### Bash Script (Git Bash/WSL)

```bash
#!/bin/bash
# teste_api.sh

BASE_URL="http://localhost:8000"

echo "=== Testando API SNCR ==="

# 1. Health Check
echo -e "\n1. Health Check..."
curl -s "$BASE_URL/health" | jq

# 2. Stats
echo -e "\n2. Estatísticas..."
curl -s "$BASE_URL/stats" | jq

# 3. Buscar imóvel existente
echo -e "\n3. Buscar imóvel 12345678901234567..."
curl -s "$BASE_URL/imovel/12345678901234567" | jq

# 4. Buscar imóvel não existente
echo -e "\n4. Buscar imóvel inexistente..."
curl -s -w "\nStatus: %{http_code}\n" "$BASE_URL/imovel/99999999999999999" | jq

# 5. Código inválido
echo -e "\n5. Código inválido..."
curl -s -w "\nStatus: %{http_code}\n" "$BASE_URL/imovel/123" | jq

echo -e "\n=== Testes Concluídos ==="
```

**Executar**:
```bash
chmod +x teste_api.sh
./teste_api.sh
```

---

## 📊 Testando Performance

### Benchmark com PowerShell

```powershell
# benchmark_api.ps1
$BASE_URL = "http://localhost:8000"
$CODIGO = "12345678901234567"
$REQUESTS = 100

Write-Host "=== Benchmark: $REQUESTS requisições ===" -ForegroundColor Green

$times = @()

for ($i = 1; $i -le $REQUESTS; $i++) {
    $start = Get-Date
    
    try {
        Invoke-RestMethod -Uri "$BASE_URL/imovel/$CODIGO" -Method Get | Out-Null
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        $times += $duration
        
        if ($i % 10 -eq 0) {
            Write-Host "Progresso: $i/$REQUESTS" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Erro na requisição $i" -ForegroundColor Red
    }
}

# Estatísticas
$min = ($times | Measure-Object -Minimum).Minimum
$max = ($times | Measure-Object -Maximum).Maximum
$avg = ($times | Measure-Object -Average).Average
$p95 = ($times | Sort-Object)[[int]($REQUESTS * 0.95)]

Write-Host "`n=== Resultados ===" -ForegroundColor Green
Write-Host "Total de requisições: $REQUESTS" -ForegroundColor Cyan
Write-Host "Tempo mínimo: $([math]::Round($min, 2)) ms" -ForegroundColor White
Write-Host "Tempo máximo: $([math]::Round($max, 2)) ms" -ForegroundColor White
Write-Host "Tempo médio: $([math]::Round($avg, 2)) ms" -ForegroundColor White
Write-Host "Percentil 95: $([math]::Round($p95, 2)) ms" -ForegroundColor White
Write-Host "Throughput: $([math]::Round($REQUESTS / ($times | Measure-Object -Sum).Sum * 1000, 2)) req/s" -ForegroundColor White
```

**Executar**:
```powershell
.\benchmark_api.ps1
```

**Resultado Esperado**:
```
=== Resultados ===
Total de requisições: 100
Tempo mínimo: 5.23 ms
Tempo máximo: 45.67 ms
Tempo médio: 12.45 ms
Percentil 95: 25.30 ms
Throughput: 80.32 req/s
```

---

## 🌐 Documentação Interativa

### Swagger UI

Abra no navegador:
```
http://localhost:8000/docs
```

- ✅ Interface interativa
- ✅ Tente todos os endpoints
- ✅ Veja schemas automaticamente
- ✅ Baixe OpenAPI spec

### ReDoc

Abra no navegador:
```
http://localhost:8000/redoc
```

- ✅ Documentação mais limpa
- ✅ Melhor para leitura
- ✅ Exportação PDF (browser)

---

## 🔐 Anonimização de CPF

### Como Funciona

| CPF Original | CPF na API | Explicação |
|--------------|------------|------------|
| `12345678972` | `***.***.*72-72` | Últimos 2 dígitos + verificador |
| `98765432109` | `***.***.*10-09` | Últimos 2 dígitos + verificador |
| `11122233344` | `***.***.*44-44` | Últimos 2 dígitos + verificador |

**Regex aplicado**:
```python
# Formato: ***.***.*DD-VV
# DD = dígitos 8-9 (últimos 2 antes do verificador)
# VV = dígitos 10-11 (verificador)
```

---

## 🐛 Depuração

### Ver Logs da API

```powershell
docker-compose logs -f api
```

### Ver Logs Estruturados

```powershell
docker-compose exec api cat logs/sncr_$(Get-Date -Format "yyyy-MM-dd").log | jq
```

### Conectar ao Banco Diretamente

```powershell
docker-compose exec postgres psql -U sncr_user -d sncr_db

# Queries úteis:
SELECT * FROM imoveis LIMIT 5;
SELECT COUNT(*) FROM pessoas;
\d+ imoveis  -- Descreve tabela com índices
```

---

## 📝 Notas

- **Rate Limiting**: Atualmente não implementado
- **Autenticação**: Atualmente não implementado
- **Cache**: Consultas sempre vão ao banco
- **CORS**: Habilitado para todos os origins (dev only)

---

**Última atualização**: 2026-03-30
