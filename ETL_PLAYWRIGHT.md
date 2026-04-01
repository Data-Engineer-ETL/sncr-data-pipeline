# ETL com Playwright - Guia Completo

## 🎯 Visão Geral

A nova ETL usa **Playwright** para automação completa do navegador, substituindo o scraper HTTP básico. Isso permite:

- ✅ **Resolver captchas automaticamente** (lê texto exibido na página)
- ✅ **Executar JavaScript** (sites dinâmicos funcionam perfeitamente)
- ✅ **Download de CSVs** com gerenciamento automático de arquivos
- ✅ **Robustez** contra mudanças no site

## 🚀 Início Rápido

### 1. Instalar Playwright

```powershell
# Instalar pacote Python
pip install playwright

# Baixar navegador Chromium
python -m playwright install chromium
```

### 2. Executar ETL Completa

```powershell
# Modo headless (sem interface, mais rápido)
python scripts/run_etl_playwright.py

# Com interface (vê o navegador trabalhando)
python scripts/run_etl_playwright.py --visible

# Especificar estados
python scripts/run_etl_playwright.py SP MG RJ

# Apenas carregar CSVs existentes (sem download)
python scripts/run_etl_playwright.py --skip-download
```

## 📋 Fluxo de Execução

### Fase 1: Download de CSVs 📥

O Playwright automatiza o navegador para:
1. Navegar para página SNCR
2. Clicar em "Dados Abertos"
3. **Resolver captcha** (lê números exibidos, remove espaços, preenche input)
4. Selecionar estado
5. Baixar CSV para `data_download/UF/SNCR_UF.csv`

### Fase 2: Carga no Banco de Dados 💾

Para cada CSV baixado:
1. Lê arquivo CSV
2. Transforma em modelos de domínio (Pydantic)
3. Valida dados (CPF 11 dígitos, código INCRA 17 dígitos)
4. Carrega no PostgreSQL com **idempotência** (upsert)
5. Registra metadata da extração

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│  scripts/run_etl_playwright.py                      │
│  (Orchestração da pipeline)                         │
└─────────────┬───────────────────────────────────────┘
              │
              ├──► src/adapters/scraper_playwright.py
              │    (Automação do navegador)
              │    - Navegação
              │    - Resolução de captcha
              │    - Download de CSVs
              │
              ├──► pandas (Leitura de CSV)
              │
              ├──► src/domain/models.py
              │    (Validação com Pydantic)
              │
              └──► src/adapters/repository.py
                   (Persistência idempotente)
```

## 📊 Estrutura de Arquivos

```
data_download/
├── SP/
│   └── SNCR_SP.csv
├── MG/
│   └── SNCR_MG.csv
└── RJ/
    └── SNCR_RJ.csv
```

## 🔧 Opções de Configuração

### Modo Headless vs Visível

```python
# Headless (sem interface) - Produção
pipeline = PlaywrightETLPipeline(headless=True)

# Visível (com interface) - Debug/Demo
pipeline = PlaywrightETLPipeline(headless=False)
```

### Skip Download

Use quando já tem CSVs baixados e quer apenas carregar no banco:

```powershell
python scripts/run_etl_playwright.py --skip-download
```

### Estados Customizados

```powershell
# Apenas um estado
python scripts/run_etl_playwright.py SP

# Múltiplos estados
python scripts/run_etl_playwright.py SP MG RJ BA PR

# Todos os estados configurados em .env
python scripts/run_etl_playwright.py
```

## 🐳 Docker

Atualizar o `docker-compose.yml` para usar a nova ETL:

```yaml
services:
  etl:
    build: .
    command: python scripts/run_etl_playwright.py
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=${DATABASE_URL}
    profiles:
      - etl
```

Executar:

```bash
docker-compose --profile etl up
```

## 🔍 Logs e Monitoramento

A ETL usa **Loguru** para logs estruturados:

```
17:58:01 | INFO | 🚀 ETL Pipeline inicializado (modo Playwright)
17:58:01 | INFO | 📥 FASE 1: Download de CSVs com Playwright
17:58:06 | INFO | 📝 Captcha detectado: '8 3 4 7 0' → '83470'
17:58:06 | INFO | ✅ Captcha resolvido
17:58:07 | INFO | ✅ Estado SP selecionado
17:58:08 | INFO | ✅ CSV baixado: data_download\SP\SNCR_SP.csv
17:58:08 | INFO | 📊 FASE 2: Carga no banco de dados
17:58:08 | INFO | 📖 Lendo CSV: data_download\SP\SNCR_SP.csv
17:58:08 | INFO | 📊 CSV contém 1500 registros
17:58:08 | INFO | ✅ Transformados 500 imóveis
17:58:09 | INFO | 💾 Carregados 500 imóveis para Todos/SP
17:58:10 | INFO | 📈 ESTATÍSTICAS FINAIS
17:58:10 | INFO | 🏠 Total de imóveis: 500
17:58:10 | INFO | 👥 Total de pessoas: 1200
17:58:10 | INFO | 🔗 Total de vínculos: 1500
```

## ⚠️ Troubleshooting

### Erro: Certificate Issues

```powershell
# Instalar Chromium ignorando certificados SSL
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
python -m playwright install chromium
```

### Erro: Timeout ao Resolver Captcha

- Verifique se o seletor `#captcha-text-export` está correto
- Aumente timeout em `resolver_captcha()` se rede estiver lenta
- Use `--visible` para ver o que está acontecendo

### Erro: CSV Não Encontrado

```powershell
# Verificar arquivos baixados
ls data_download/*/

# Rodar apenas download
python scripts/run_etl_playwright.py --visible

# Depois carregar
python scripts/run_etl_playwright.py --skip-download
```

### Erro: Banco de Dados

```powershell
# Verificar se PostgreSQL está rodando
docker-compose ps

# Verificar conexão
docker-compose exec postgres psql -U sncr -d sncr_db -c "SELECT COUNT(*) FROM imoveis;"
```

## 🆚 Comparação: HTTP vs Playwright

| Aspecto | HTTP Scraper (Antigo) | Playwright (Novo) |
|---------|----------------------|-------------------|
| **JavaScript** | ❌ Não suporta | ✅ Executa completamente |
| **Captcha** | ❌ Não resolve | ✅ Resolve automaticamente |
| **Robustez** | ⚠️ Frágil | ✅ Muito robusto |
| **Velocidade** | ⚡ Muito rápido | 🐢 Mais lento (navegador) |
| **Recursos** | 💡 Leve | 🖥️ Pesado (navegador completo) |
| **Debug** | 😵 Difícil | 👀 Visual (modo --visible) |
| **Manutenção** | 🔧 Requer ajustes frequentes | ✅ Mais estável |

## 🎯 Quando Usar Cada Um

### Use HTTP Scraper (scripts/run_etl.py)
- Site simples sem JavaScript
- Não tem captcha
- Precisa de alta velocidade
- Ambiente com recursos limitados

### Use Playwright (scripts/run_etl_playwright.py)
- **Site tem JavaScript** ✅
- **Precisa resolver captcha** ✅ (nosso caso!)
- Site muda frequentemente
- Precisa de robustez máxima
- Desenvolvimento/debug visual

## 📚 Referências

- [Playwright Documentation](https://playwright.dev/python/)
- [Async/Await em Python](https://docs.python.org/3/library/asyncio.html)
- [Clean Architecture](ARCHITECTURE.md)
- [Troubleshooting Geral](TROUBLESHOOTING_IMPORTS.md)

## 🤝 Contribuindo

Para adicionar suporte a novos elementos do site:

1. Inspecione página com DevTools (F12)
2. Identifique seletores CSS (#id, .class, [data-attr])
3. Adicione métodos em `SNCRPlaywrightScraper`
4. Teste com `--visible` para debug visual

Exemplo:

```python
async def clicar_novo_botao(self) -> bool:
    """Clica em um novo botão do site."""
    try:
        await self.page.click('#novo-botao', timeout=5000)
        return True
    except Exception as e:
        logger.error(f"Erro ao clicar: {e}")
        return False
```

---

**Pronto para extrair dados com captcha? Execute:**

```powershell
python scripts/run_etl_playwright.py --visible
```
