# 🚀 Quick Start Atualizado - ETL com Playwright

## 📌 O Que Mudou?

A extração agora usa **Playwright** para automação completa do navegador! Isso resolve captchas automaticamente e funciona perfeitamente com sites JavaScript-heavy.

## ⚡ Início Ultra-Rápido

### 1️⃣ Instalar Dependências

```powershell
# Ativar ambiente virtual (se necessário)
.venv\Scripts\Activate.ps1

# Instalar Playwright
pip install playwright

# Baixar navegador Chromium
python -m playwright install chromium
```

**Nota**: Se der erro de certificado SSL:
```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
python -m playwright install chromium
```

### 2️⃣ Rodar ETL Completa

```powershell
# Ver o navegador trabalhando (recomendado primeira vez)
python scripts/run_etl_playwright.py --visible

# Modo produção (headless, sem interface)
python scripts/run_etl_playwright.py
```

### 3️⃣ Verificar Resultados

```powershell
# Ver CSVs baixados
ls data_download\

# Verificar banco de dados
docker-compose exec postgres psql -U sncr_user -d sncr_db

# Dentro do psql:
SELECT COUNT(*) FROM imoveis;
SELECT COUNT(*) FROM pessoas;
SELECT uf, COUNT(*) FROM imoveis GROUP BY uf;
```

## 🎯 Comandos Úteis

### Extrair Estados Específicos

```powershell
# Apenas São Paulo
python scripts/run_etl_playwright.py SP

# Múltiplos estados
python scripts/run_etl_playwright.py SP MG RJ BA PR
```

### Apenas Carregar CSVs Existentes

```powershell
# Se já tem os CSVs, pula o download
python scripts/run_etl_playwright.py --skip-download
```

### Com Docker

```bash
# ETL Playwright completa
docker-compose --profile etl-playwright up

# Ver logs em tempo real
docker-compose --profile etl-playwright up etl-playwright --attach

# Rodar em background
docker-compose --profile etl-playwright up -d
```

## 📊 O Que Você Verá

```
🚀 ETL Pipeline inicializado (modo Playwright)
📥 FASE 1: Download de CSVs com Playwright
======================================================================
🌐 Abrindo navegador...
✅ Navegador iniciado
======================================================================
Extraindo dados: SP
======================================================================
🌐 Acessando https://...
✅ Página carregada
🔗 Clicando em 'Dados Abertos'...
✅ Página 'Dados Abertos' acessada
🔐 Resolvendo captcha...
📝 Captcha detectado: '8 3 4 7 0' → '83470'
✅ Captcha resolvido
🌍 Selecionando estado: SP
✅ Estado SP selecionado
📥 Iniciando download do CSV...
⏳ Aguardando download...
✅ CSV baixado: data_download\SP\SNCR_SP.csv
✅ Extração concluída: data_download\SP\SNCR_SP.csv

======================================================================
📊 FASE 2: Carga no banco de dados
======================================================================
📖 Lendo CSV: data_download\SP\SNCR_SP.csv
📊 CSV contém 1500 registros
✅ Transformados 500 imóveis
💾 Carregados 500 imóveis para Todos/SP

======================================================================
📈 ESTATÍSTICAS FINAIS
======================================================================
🏠 Total de imóveis: 500
👥 Total de pessoas: 1200
🔗 Total de vínculos: 1500
🗺️ Estados processados: 1
🏘️ Municípios processados: 1

✅ Extração concluída com sucesso!
👋 ETL Pipeline finalizado
```

## 🐛 Troubleshooting Rápido

### Erro: ModuleNotFoundError: No module named 'playwright'

```powershell
pip install playwright
```

### Erro: Executable doesn't exist at /path/to/chromium

```powershell
python -m playwright install chromium
```

### Erro: Timeout ao resolver captcha

- Site pode estar lento - aumente timeout
- Ou use modo `--visible` para ver o que está acontecendo:

```powershell
python scripts/run_etl_playwright.py --visible
```

### CSV Baixado Mas Não Carregado

```powershell
# Verificar estrutura do CSV
Get-Content data_download\SP\SNCR_SP.csv | Select-Object -First 5

# Forçar recarga
python scripts/run_etl_playwright.py --skip-download
```

### Banco de Dados Não Conecta

```powershell
# Iniciar PostgreSQL
docker-compose up -d postgres

# Aguardar 10 segundos
Start-Sleep 10

# Testar conexão
docker-compose exec postgres pg_isready
```

## 🔄 Migração do Antigo

Se você estava usando o ETL HTTP antigo:

1. ✅ **Mesma estrutura de banco** - não precisa recriar
2. ✅ **Mesma API** - endpoints idênticos
3. ✅ **Dados compatíveis** - CSV tem mesmas colunas
4. ⚠️ **Nova dependência** - instalar Playwright

```powershell
# Apenas instale Playwright e use o novo script
pip install playwright
python -m playwright install chromium
python scripts/run_etl_playwright.py
```

## 📚 Documentação Completa

- **Detalhes técnicos**: [ETL_PLAYWRIGHT.md](ETL_PLAYWRIGHT.md)
- **Arquitetura**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Troubleshooting**: [TROUBLESHOOTING_IMPORTS.md](TROUBLESHOOTING_IMPORTS.md)
- **README geral**: [README.md](README.md)

## 🎉 Pronto!

Você está usando a versão mais robusta e moderna da ETL! 🚀

**Próximos passos**:
1. ✅ Dados extraídos e carregados
2. 🌐 Acessar API: http://localhost:8000
3. 📊 Ver documentação: http://localhost:8000/docs
4. 🔍 Consultar dados via API

```bash
# Exemplo de consulta
curl http://localhost:8000/stats
curl "http://localhost:8000/imovel/12345678901234567"
```

---

**Dúvidas?** Consulte [ETL_PLAYWRIGHT.md](ETL_PLAYWRIGHT.md) para guia completo!
