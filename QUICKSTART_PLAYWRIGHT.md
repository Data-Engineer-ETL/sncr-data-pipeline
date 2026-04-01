# 🚀 Quick Start - Baixar CSVs com Automação

Execute estes comandos no PowerShell para começar:

```powershell
# 1. Entre no diretório
cd C:\code\challange

# 2. Ative ambiente virtual
.\venv\Scripts\activate

# 3. Instale Playwright
pip install playwright

# 4. Instale navegador Chromium (~200MB, uma vez)
python -m playwright install chromium

# 5. Execute!
python scraper_playwright.py
```

**Escolha modo 1** (com interface) na primeira vez para ver a mágica acontecer! 🎩✨

---

## 🎯 O que vai acontecer:

1. 🌐 Navegador abre automaticamente
2. 🔍 Acessa o site SNCR
3. 📊 Clica em "Dados Abertos"
4. 🔢 **Resolve o captcha sozinho!** (ex: "4 8 9 2 7" → 48927)
5. 🗺️ Seleciona o estado (SP)
6. ⬇️ Clica em "Baixar CSV"
7. 💾 Salva em `data_download/SP/`
8. ✅ Pronto!

**Tempo**: ~10-15 segundos por estado

---

## 📁 Resultado

Após executar, você terá:

```
C:\code\challange\
└── data_download\
    └── SP\
        └── imoveis_SP_todos.csv   ← Seus dados!
```

---

## 🎓 Documentação Completa

- **Guia completo**: [PLAYWRIGHT_GUIDE.md](PLAYWRIGHT_GUIDE.md)
- **Troubleshooting**: Veja os erros comuns no guia
- **Personalizar**: Como extrair outros estados/municípios

---

## ⚡ Dicas Rápidas

### Extrair mais estados:

Edite `scraper_playwright.py`, linha 280:
```python
estados = ['SP', 'MG', 'RJ']  # Adicione quantos quiser!
```

### Modo headless (mais rápido):

Escolha opção **2** quando perguntar

### Ver o que está acontecendo:

Escolha opção **1** - você verá o navegador em ação!

---

**Ready? Execute agora:** `python scraper_playwright.py` 🚀
