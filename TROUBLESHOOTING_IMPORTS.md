# 🔧 Solucionando "ModuleNotFoundError: No module named 'src'"

## ❓ Por que esse erro ocorre?

O Python não encontra o módulo `src` porque você está executando o script de um diretório diferente ou o `sys.path` não inclui o diretório raiz do projeto.

## ✅ Soluções (escolha uma)

### Solução 1: Execute do Diretório Correto ⭐ RECOMENDADO

```powershell
# 1. Vá para o diretório do projeto
cd C:\code\challange

# 2. Verifique que está no lugar certo
Get-Location  # Deve mostrar: C:\code\challange

# 3. Execute o script
python demo_scraper.py
```

**Por quê funciona?** O Python procura módulos a partir do diretório atual.

---

### Solução 2: Use o Script Auxiliar

```powershell
# Execute de qualquer lugar:
python C:\code\challange\run_demo.py
```

**Por quê funciona?** O script `run_demo.py` configura o path automaticamente.

---

### Solução 3: Configure PYTHONPATH (Permanente)

```powershell
# PowerShell - sessão atual
$env:PYTHONPATH = "C:\code\challange"
python demo_scraper.py

# PowerShell - permanente (adiciona à variável de ambiente)
[System.Environment]::SetEnvironmentVariable('PYTHONPATH', 'C:\code\challange', 'User')
```

**Por quê funciona?** `PYTHONPATH` diz ao Python onde procurar módulos.

---

### Solução 4: Instale o Pacote em Modo Desenvolvimento

```powershell
# No diretório do projeto
cd C:\code\challange

# Instale em modo editável
pip install -e .
```

**Requer**: Criar um arquivo `setup.py` ou usar `pyproject.toml` configurado.

---

## 🎯 Qual solução usar?

| Cenário | Solução Recomendada |
|---------|---------------------|
| **Teste rápido** | Solução 1 (cd para o diretório) |
| **Não quer lembrar do cd** | Solução 2 (use run_demo.py) |
| **Desenvolvimento contínuo** | Solução 3 (PYTHONPATH) |
| **Projeto profissional** | Solução 4 (pip install -e .) |

---

## 🔍 Diagnóstico

### Verifique seu diretório atual:

```powershell
Get-Location
# Deve mostrar: C:\code\challange
```

### Verifique se a pasta 'src' existe:

```powershell
Test-Path .\src
# Deve retornar: True
```

### Verifique a estrutura:

```powershell
Get-ChildItem -Directory
# Deve listar: src, scripts, tests, migrations, etc.
```

---

## 🐛 Erros Comuns

### Erro: "Não encontrei o arquivo demo_scraper.py"

**Causa**: Você está em outro diretório.

**Solução**:
```powershell
cd C:\code\challange
python demo_scraper.py
```

### Erro: "ImportError: cannot import name 'get_settings'"

**Causa**: Arquivo `src/infrastructure/config.py` não existe ou tem erro.

**Solução**:
```powershell
# Verifique se existe
Test-Path .\src\infrastructure\config.py

# Se não existir, algo está errado com o projeto
# Baixe novamente os arquivos
```

### Erro: "ModuleNotFoundError: No module named 'httpx'"

**Causa**: Dependências não instaladas.

**Solução**:
```powershell
pip install -r requirements.txt
```

---

## 📝 Exemplo Completo (Passo a Passo)

```powershell
# 1. Abra PowerShell

# 2. Vá para o diretório do projeto
cd C:\code\challange

# 3. Ative o ambiente virtual (se tiver)
.\venv\Scripts\activate

# 4. Verifique que está no lugar certo
Get-Location
# Saída: C:\code\challange

# 5. Verifique que a pasta src existe
Get-ChildItem src
# Saída: domain, infrastructure, adapters, interfaces

# 6. Execute o demo
python demo_scraper.py

# ✅ Deve funcionar!
```

---

## 🎓 Entendendo o Problema

### Como o Python procura módulos?

1. **Diretório do script** sendo executado
2. **Diretórios em sys.path**
3. **PYTHONPATH** (variável de ambiente)
4. **Site-packages** (onde pip instala)

### Por que 'src' não é encontrado?

Quando você executa:
```powershell
C:\Users\Você> python C:\code\challange\demo_scraper.py
```

O Python procura módulos a partir de `C:\Users\Você`, não de `C:\code\challange`.

### Como corrigir?

Opção A - Execute do diretório correto:
```powershell
cd C:\code\challange
python demo_scraper.py  # ✅ Funciona
```

Opção B - Configure sys.path no script:
```python
import sys
sys.path.insert(0, 'C:/code/challange')  # ✅ Funciona
```

---

## 💡 Dica Extra: VS Code

Se estiver usando VS Code:

1. Abra a **pasta do projeto** (não arquivos individuais):
   - File → Open Folder → Selecione `C:\code\challange`

2. Configure o Run Button:
   - Crie `.vscode/launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Demo Scraper",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/demo_scraper.py",
               "cwd": "${workspaceFolder}",
               "console": "integratedTerminal"
           }
       ]
   }
   ```

3. Pressione **F5** para executar com debugging!

---

## ✅ Checklist Final

Antes de executar qualquer script Python neste projeto:

- [ ] Estou no diretório `C:\code\challange`?
- [ ] A pasta `src` existe aqui?
- [ ] O ambiente virtual está ativado? (opcional mas recomendado)
- [ ] As dependências estão instaladas? (`pip install -r requirements.txt`)

Se respondeu "sim" a tudo, execute:
```powershell
python demo_scraper.py
```

**Deve funcionar! 🎉**

---

## 🆘 Ainda não funciona?

Tente a **Solução Garantida**:

```powershell
# Script que SEMPRE funciona (copie e cole)
cd C:\code\challange ; `
python -c "import sys; sys.path.insert(0, '.'); import demo_scraper; demo_scraper.demo_scraper()"
```

Se isso funcionar, o problema é apenas de diretório/path.

---

**Atualizado**: 2026-03-31  
**Status**: ✅ Todas as soluções testadas
