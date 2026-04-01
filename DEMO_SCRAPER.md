# 🔍 Como Testar o Scraper (Sem Banco de Dados)

Este guia mostra como testar **apenas a parte de extração/scraper** sem precisar de PostgreSQL ou Docker.

## ⚡ Execução Rápida

```powershell
# Certifique-se de estar no ambiente virtual
.\venv\Scripts\activate

# Execute a demonstração
python demo_scraper.py
```

## 📋 O que o script faz:

1. ✅ **Inicializa sessão HTTP** com o site SNCR
2. ✅ **Lista municípios** do primeiro estado configurado
3. ✅ **Baixa dados CSV** de 1 município (demonstração)
4. ✅ **Mostra preview** dos dados extraídos
5. ✅ **Salva CSV** para você inspecionar no Excel
6. ✅ **Não salva no banco** - apenas demonstração

## 🎬 Saída Esperada

```
======================================================================
🔍 DEMONSTRAÇÃO DO SCRAPER SNCR
======================================================================

Este script demonstra a extração de dados do site SNCR
Os dados serão apenas exibidos no console (sem salvar no banco)

📍 Site alvo: https://data-engineer-challenge-production.up.railway.app
🌎 Estados configurados: SP,MG,RJ
🔄 Max retries: 5
⏱️  Timeout: 30s
💾 Checkpoint dir: ./checkpoints

──────────────────────────────────────────────────────────────────────
Para demonstração, vamos extrair apenas 1 município de 1 estado.
──────────────────────────────────────────────────────────────────────

🎯 Estado selecionado: SP

🚀 Iniciando scraper...

1️⃣  Inicializando sessão HTTP...
   ✅ Sessão inicializada

2️⃣  Buscando municípios de SP...
   ✅ Encontrados 5 municípios:
      1. São Paulo
      2. Campinas
      3. Santos
      4. Ribeirão Preto
      5. Sorocaba

3️⃣  Extraindo dados de São Paulo/SP...
   ⏳ Baixando CSV... (pode levar alguns segundos)
   ✅ Dados extraídos com sucesso!

📊 ESTATÍSTICAS DOS DADOS EXTRAÍDOS
──────────────────────────────────────────────────────────────────────
   Total de registros: 150
   Colunas: ['codigo_incra', 'area_ha', 'situacao', 'cpf', ...]

📄 PREVIEW DOS DADOS (primeiras 3 linhas)
──────────────────────────────────────────────────────────────────────
   codigo_incra   area_ha  situacao         cpf  ...
0  12345678901234567  142.50    Ativo  123.456.789-01  ...
1  98765432109876543   85.75    Ativo  987.654.321-09  ...
...

💾 Dados salvos em: demo_data_SP_São_Paulo.csv
   👀 Você pode abrir este arquivo no Excel para inspecionar

🔍 EXEMPLO DE REGISTRO
──────────────────────────────────────────────────────────────────────
   codigo_incra: 12345678901234567
   area_ha: 142.5
   situacao: Ativo
   cpf: 123.456.789-01
   nome_completo: Maria Silva
   tipo_vinculo: Proprietário
   participacao_pct: 100.0

======================================================================
✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!
======================================================================
```

## 🔧 Configuração

### Antes de executar, verifique o `.env`:

```env
# Site alvo (já configurado)
BASE_URL=https://data-engineer-challenge-production.up.railway.app

# Estados para extrair (modifique se quiser)
TARGET_STATES=SP,MG,RJ

# Configurações de retry
MAX_RETRIES=5
RETRY_BACKOFF_FACTOR=2
REQUEST_TIMEOUT=30
```

### Se não tiver `.env`:

```powershell
# Copie o exemplo
Copy-Item .env.example .env
```

## 🎯 Personalizações

### Testar outro estado:

Edite `.env`:
```env
TARGET_STATES=MG  # Testará apenas Minas Gerais
```

### Ver logs detalhados:

Edite `demo_scraper.py`, linha que tem `level="WARNING"`:
```python
level="INFO",  # Muda WARNING para INFO
```

### Extrair mais municípios:

Edite `demo_scraper.py`, procure por:
```python
municipio = municipios[0]  # Primeiro município
```

E mude para um loop:
```python
for municipio in municipios[:3]:  # Primeiros 3 municípios
    print(f"Extraindo {municipio}...")
    df = scraper.download_csv(uf, municipio)
    # ... resto do código
```

## 🐛 Problemas Comuns

### "Site indisponível ou usa captcha"

**Causa**: O site SNCR simulado pode estar offline ou com proteção anti-bot.

**Solução**:
1. Verifique se o site está acessível: https://data-engineer-challenge-production.up.railway.app
2. Aguarde alguns minutos (pode estar com rate limit)
3. Tente novamente

### "Nenhum município encontrado"

**Causa**: O scraper não conseguiu parsear a página HTML.

**Solução**:
1. O script usa fallback (lista hardcoded de municípios)
2. Ainda assim tentará baixar dados
3. Se persistir, o site pode ter mudado estrutura

### "Timeout de rede"

**Causa**: Conexão lenta ou site lento.

**Solução**: Aumente timeout no `.env`:
```env
REQUEST_TIMEOUT=60  # 30 → 60 segundos
```

### "Module not found"

**Causa**: Dependências não instaladas.

**Solução**:
```powershell
pip install -r requirements.txt
```

## 📁 Arquivos Gerados

Após executar, você terá:

```
c:\code\challange\
├── demo_data_SP_São_Paulo.csv  # Dados extraídos (Excel)
├── checkpoints/                # (vazio, demo não usa)
└── logs/                       # Logs detalhados
    └── sncr_YYYY-MM-DD.log
```

**Abra o CSV no Excel** para ver toda a estrutura dos dados!

## 🎓 Entendendo o Scraper

### Fluxo de Execução:

```
1. SNCRScraper.__init__()
   ↓
2. initialize_session() 
   → Visita homepage, configura cookies
   ↓
3. get_municipios(uf)
   → Faz request para /export
   → Parseia HTML (BeautifulSoup)
   → Retorna lista de municípios
   ↓
4. download_csv(uf, municipio)
   → POST /export com form data
   → Parse CSV com pandas
   → Retorna DataFrame
   ↓
5. DataFrame exibido no console
```

### Recursos Implementados:

- ✅ **Retry com backoff exponencial**: 5 tentativas, espera 2^n segundos
- ✅ **Detecção de anti-bot**: Identifica páginas de desafio
- ✅ **Session management**: Mantém cookies entre requests
- ✅ **Rate limiting**: 1 segundo entre requests
- ✅ **Timeout configurável**: 30s padrão
- ✅ **User-Agent realista**: Parece navegador real
- ✅ **Logging estruturado**: JSON para análise

### Código Relevante:

**Retry**: `@retry(stop=stop_after_attempt(5), ...)`  
**Anti-bot**: `_is_bot_challenge(response)`  
**Session**: `httpx.Client(timeout=..., headers=...)`  
**Parse CSV**: `pd.read_csv(StringIO(csv_content))`

## 🚀 Próximos Passos

### 1. Ver o código do scraper:

```powershell
# Abra no VS Code
code src/adapters/scraper.py
```

### 2. Testar ETL completo (com banco):

```powershell
# Com Docker (recomendado)
docker-compose --profile etl up etl

# Ou local com PostgreSQL
python scripts/run_etl.py
```

### 3. Modificar o scraper:

- Adicione novos estados em `.env`
- Ajuste timeout e retries
- Customize parsing do HTML
- Adicione novos campos ao CSV

## 💡 Dicas

### Performance:

- O scraper espera 1s entre requests (ser educado com o servidor)
- Retry acontece automaticamente em falhas
- Checkpoints salvam progresso (não usado na demo)

### Desenvolvimento:

```powershell
# Instale Playwright para scraping avançado (opcional)
pip install playwright
python -m playwright install chromium

# Útil para sites com JavaScript pesado
```

### Debug:

```powershell
# Veja logs detalhados
Get-Content logs/sncr_$(Get-Date -Format 'yyyy-MM-dd').log | Select-String "ERROR"
```

## ❓ FAQ

**P: Quanto tempo demora para extrair todos os municípios?**  
R: ~5-15 minutos (depende de quantos municípios e da velocidade do site).

**P: Os dados são salvos automaticamente?**  
R: Nesta demo, NÃO. Use `run_etl.py` para salvar no PostgreSQL.

**P: Posso extrair dados de outros sites?**  
R: Sim! Modifique `BASE_URL` no `.env` e adapte o scraper.

**P: É legal fazer scraping?**  
R: Este é um site simulado para o desafio. Em produção, sempre respeite robots.txt e termos de uso.

---

**Criado em**: 2026-03-30  
**Status**: ✅ Funcional sem banco de dados

**Divirta-se explorando o scraper! 🕷️**
