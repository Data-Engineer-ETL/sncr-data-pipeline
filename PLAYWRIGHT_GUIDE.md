# 🤖 Automação com Playwright - SNCR

Este guia mostra como usar **Playwright** para automatizar o download de CSVs do SNCR, incluindo resolução automática de captcha.

## ⚡ Instalação

```powershell
# 1. Instale Playwright
pip install playwright

# 2. Instale o navegador Chromium
python -m playwright install chromium

# Aguarde o download (~200MB)
```

## 🚀 Execução

```powershell
# Certifique-se de estar no diretório do projeto
cd C:\code\challange

# Execute o scraper
python scraper_playwright.py
```

### Escolha o modo:

```
Modo de execução:
  [1] Com interface (você vê o navegador)
  [2] Sem interface (mais rápido, em background)

Escolha (1 ou 2): 1
```

- **Modo 1 (Com interface)**: Você verá o navegador abrindo e executando as ações automaticamente
- **Modo 2 (Headless)**: Executa em background, mais rápido

## 🎬 O que acontece:

1. ✅ **Abre o navegador** (Chrome)
2. ✅ **Acessa o site SNCR**
3. ✅ **Clica em "Dados Abertos"**
4. ✅ **Lê o captcha** automaticamente (ex: "4 8 9 2 7")
5. ✅ **Preenche o captcha** (48927)
6. ✅ **Seleciona o estado** (SP, MG, etc.)
7. ✅ **Clica em "Baixar CSV"**
8. ✅ **Salva o arquivo** em `data_download/`

## 📊 Saída Esperada

```
======================================================================
🤖 AUTOMAÇÃO PLAYWRIGHT - SNCR
======================================================================

Este script usa Playwright para:
  1. Navegar pela página do SNCR
  2. Clicar em 'Dados Abertos'
  3. Resolver o captcha automaticamente
  4. Selecionar estado
  5. Baixar o CSV

💡 Dica: Você verá o navegador abrindo e executando as ações!
======================================================================

🌐 Abrindo navegador (você verá a automação acontecendo)...

10:30:45 | INFO     | Iniciando Playwright...
10:30:46 | INFO     | ✅ Navegador iniciado
10:30:46 | INFO     | ======================================================================
10:30:46 | INFO     | Extraindo dados: SP
10:30:46 | INFO     | ======================================================================
10:30:46 | INFO     | Acessando https://data-engineer-challenge-production.up.railway.app...
10:30:48 | INFO     | ✅ Página carregada
10:30:48 | INFO     | ✅ Já está na página 'Dados Abertos'
10:30:48 | INFO     | ✅ Página 'Dados Abertos' acessada
10:30:48 | INFO     | Resolvendo captcha...
10:30:48 | INFO     | 📝 Captcha detectado: '4  8  9  2  7' → '48927'
10:30:49 | INFO     | ✅ Captcha resolvido
10:30:49 | INFO     | Selecionando estado: SP
10:30:50 | INFO     | ✅ Estado SP selecionado
10:30:50 | INFO     | Mantendo 'Todos os municípios'
10:30:50 | INFO     | Iniciando download do CSV...
10:30:51 | INFO     | ⏳ Aguardando download...
10:30:52 | INFO     | ✅ CSV baixado: data_download\SP\imoveis_SP_todos.csv
10:30:52 | INFO     | ✅ Extração concluída: data_download\SP\imoveis_SP_todos.csv

✅ Sucesso! Arquivo salvo em: data_download\SP\imoveis_SP_todos.csv

======================================================================
✅ AUTOMAÇÃO CONCLUÍDA
======================================================================

📁 Arquivos salvos em: ./data_download/
```

## 🎯 Personalizar Estados

Edite `scraper_playwright.py`, linha ~280:

```python
# Altere esta linha:
estados = ['SP']  # Apenas São Paulo

# Para extrair múltiplos estados:
estados = ['SP', 'MG', 'RJ']
```

## 🔧 Funcionalidades

### 1. Resolução Automática de Captcha

```python
# O script lê o texto do captcha exibido na página:
# "4  8  9  2  7" → extrai → "48927" → preenche automaticamente
```

**Como funciona:**
- Localiza o elemento `#captcha-text-export`
- Extrai o texto
- Remove espaços
- Preenche o input

### 2. Seleção de Estado e Município

```python
# Seleciona estado
await scraper.selecionar_estado('SP')

# Seleciona município específico (opcional)
await scraper.selecionar_municipio('Campinas')
```

### 3. Download do CSV

```python
# Clica no botão e aguarda o download
filepath = await scraper.baixar_csv(output_dir='data_download/SP')
```

## 🐛 Troubleshooting

### "playwright não está instalado"

```powershell
pip install playwright
python -m playwright install chromium
```

### "Timeout ao esperar captcha"

**Causa**: Página demorou para carregar.

**Solução**: Aumente o timeout no código:
```python
await self.page.wait_for_selector('#captcha-text-export', timeout=10000)  # 5000 → 10000ms
```

### "Botão de download não foi habilitado"

**Causa**: Captcha ou estado não foram preenchidos corretamente.

**Solução**: 
1. Execute em modo COM interface (`escolha 1`)
2. Veja o que está acontecendo
3. Verifique se o captcha foi resolvido

### "Navegador não abre"

**Causa**: Chromium não foi instalado.

**Solução**:
```powershell
python -m playwright install chromium --force
```

### "Download não salva"

**Causa**: Permissões de escrita.

**Solução**:
```powershell
# Crie o diretório manualmente
New-Item -ItemType Directory -Path "data_download" -Force
```

## 💡 Dicas Avançadas

### 1. Executar para Todos os Estados

```python
async def demo():
    estados = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
        'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    async with SNCRPlaywrightScraper(headless=True) as scraper:
        for uf in estados:
            print(f"\n{'='*70}")
            print(f"Processando {uf}...")
            print(f"{'='*70}\n")
            
            filepath = await scraper.extrair_estado(uf)
            
            if filepath:
                print(f"✅ {uf} concluído: {filepath}")
            else:
                print(f"❌ {uf} falhou")
            
            await asyncio.sleep(3)  # Pausa entre estados
```

### 2. Extrair Municípios Específicos

```python
# Para extrair município por município:
municipios = ['Campinas', 'Santos', 'São Paulo']

for municipio in municipios:
    filepath = await scraper.extrair_estado('SP', municipio=municipio)
```

### 3. Tirar Screenshot em Caso de Erro

```python
# Adicione no código de erro:
try:
    # ... código ...
except Exception as e:
    await self.page.screenshot(path='erro_screenshot.png')
    logger.error(f"Erro: {e}. Screenshot salvo.")
```

### 4. Modo Debug Completo

```python
# Edite o início do script:
logger.add(
    sys.stderr,
    format="<dim>{time:HH:mm:ss}</dim> | <level>{level: <8}</level> | <level>{message}</level>",
    level="DEBUG"  # INFO → DEBUG
)
```

## 📊 Vantagens sobre httpx/requests

| Recurso | httpx/requests | Playwright |
|---------|----------------|------------|
| **JavaScript** | ❌ Não executa | ✅ Executa completamente |
| **Captcha visual** | ❌ Difícil | ✅ Lê da tela |
| **Anti-bot avançado** | ❌ Bloqueado | ✅ Parece navegador real |
| **Download de arquivos** | ✅ Simples | ✅ Gerenciado |
| **Performance** | ⚡ Muito rápido | 🐢 Mais lento |
| **Recursos** | 💾 Leve | 💾 Pesado (~200MB) |

**Quando usar Playwright:**
- ✅ Site usa muito JavaScript
- ✅ Tem captcha visual
- ✅ Anti-bot detecta requests
- ✅ Precisa interagir com a página

**Quando usar httpx/requests:**
- ✅ API simples
- ✅ Performance crítica
- ✅ Não tem JavaScript complexo
- ✅ Recursos limitados

## 🎓 Aprendendo Mais

### Playwright Documentação
- https://playwright.dev/python/

### Exemplos Úteis

**Esperar elemento aparecer:**
```python
await page.wait_for_selector('#meu-elemento', state='visible')
```

**Preencher formulário:**
```python
await page.fill('#input-name', 'João Silva')
await page.select_option('#select-uf', 'SP')
await page.click('#btn-submit')
```

**Navegar páginas:**
```python
await page.goto('https://example.com')
await page.click('a[href="/outra-pagina"]')
await page.go_back()
```

**Executar JavaScript:**
```python
result = await page.evaluate('1 + 1')
print(result)  # 2
```

## 🔮 Próximos Passos

1. **Integrar com ETL**: Use este scraper no `run_etl.py`
2. **Paralelizar**: Execute múltiplos navegadores simultaneamente
3. **Retry inteligente**: Adicione retry com backoff
4. **Notificações**: Envie email quando terminar
5. **Dashboard**: Crie interface para monitorar progresso

---

**Criado em**: 2026-03-31  
**Status**: ✅ Funcional e testado

**Divirta-se automatizando! 🤖**
