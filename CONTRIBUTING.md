# Contribuindo para o SNCR Pipeline

Obrigado por considerar contribuir! Este documento fornece diretrizes para contribuições.

## Código de Conduta

- Seja respeitoso e profissional
- Foque no problema técnico, não na pessoa
- Aceite feedback construtivo
- Priorize o bem do projeto

## Como Contribuir

### Reportando Bugs

Abra uma issue com:
- **Título claro**: resumo do problema
- **Descrição**: o que aconteceu vs. o esperado
- **Passos para reproduzir**: comandos exatos executados
- **Ambiente**: OS, versão do Python/Docker
- **Logs**: erros relevantes (use ```bash blocks)

### Sugerindo Features

Abra uma issue com:
- **Motivação**: por que esta feature é útil?
- **Proposta**: como deveria funcionar?
- **Alternativas**: outras abordagens consideradas?

### Pull Requests

1. **Fork** o repositório
2. **Crie um branch**: `git checkout -b feature/minha-feature`
3. **Desenvolva** seguindo os padrões abaixo
4. **Teste**: rode `pytest` e garanta que passa
5. **Commit**: mensagens claras (veja convenção abaixo)
6. **Push**: `git push origin feature/minha-feature`
7. **Abra PR**: descreva mudanças e motivação

## Padrões de Código

### Python

- **PEP 8**: use `black` e `ruff`
- **Type hints**: obrigatório em funções públicas
- **Docstrings**: formato Google style
- **Imports**: organize com `isort`

Exemplo:
```python
from typing import Optional

def get_imovel(codigo: str) -> Optional[dict]:
    """
    Retrieve property by INCRA code.
    
    Args:
        codigo: 17-digit INCRA code
    
    Returns:
        Property dict or None if not found
    
    Raises:
        ValueError: If codigo is invalid
    """
    ...
```

### Formatação

```bash
# Auto-format
black src/ tests/
ruff check src/ tests/ --fix

# Type check
mypy src/
```

### Commits

Siga [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<escopo>): <descrição curta>

<corpo opcional>

<rodapé opcional>
```

**Tipos**:
- `feat`: nova feature
- `fix`: correção de bug
- `docs`: documentação
- `style`: formatação
- `refactor`: refatoração
- `test`: testes
- `chore`: tarefas de build/config

**Exemplos**:
```
feat(api): add CPF anonymization endpoint
fix(scraper): handle timeout errors correctly
docs(readme): update installation steps
```

### Testes

- **Coverage**: mantenha > 80%
- **Fixtures**: reutilize em `conftest.py`
- **Asserts**: use pytest asserts naturais
- **Nomes**: `test_<função>_<cenário>_<resultado>`

Exemplo:
```python
def test_imovel_validate_codigo_invalid_length_raises_error():
    """Test that invalid codigo length raises ValueError."""
    with pytest.raises(ValueError, match="17 dígitos"):
        Imovel(codigo_incra="123", ...)
```

### Documentação

- **Docstrings**: todas as funções públicas
- **README**: atualize se adicionar features
- **CHANGELOG**: documente mudanças
- **Type hints**: ajudam mais que comentários

## Estrutura de Branches

- `main`: código estável, sempre deployável
- `develop`: desenvolvimento ativo
- `feature/*`: novas features
- `fix/*`: correções de bugs
- `docs/*`: documentação

## Processo de Review

PR será revisado quanto a:
1. **Qualidade**: código limpo, idiomático
2. **Testes**: cobertura adequada
3. **Documentação**: clara e atualizada
4. **Performance**: não introduz regressões
5. **Segurança**: sem vulnerabilidades

## Ambientes

### Desenvolvimento

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pre-commit install  # se usar pre-commit
```

### Testes

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage
pytest --cov=src --cov-report=html
```

### Linting

```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Dúvidas?

- Abra uma issue com label `question`
- Consulte a documentação (README, ARCHITECTURE)
- Veja PRs anteriores para exemplos

---

**Obrigado por contribuir! 🚀**
