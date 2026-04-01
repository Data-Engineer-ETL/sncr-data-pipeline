"""
Valida configuração de variáveis de ambiente.
Execute: python validate_config.py
"""
import os
import sys
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


REQUIRED_VARS = [
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

OPTIONAL_VARS = [
    'API_WORKERS',
    'MAX_RETRIES',
    'RETRY_BACKOFF_FACTOR',
    'REQUEST_TIMEOUT',
    'CHECKPOINT_DIR',
    'LOG_LEVEL',
]

DEFAULT_VALUES_WARNING = {
    'POSTGRES_PASSWORD': 'change_me_in_production',
}


def print_status(message: str, status: str = "info"):
    """Print formatted status message."""
    colors = {
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
        "info": BLUE,
    }
    symbols = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }
    color = colors.get(status, RESET)
    symbol = symbols.get(status, "•")
    print(f"{color}{symbol} {message}{RESET}")


def validate_config() -> bool:
    """Valida configuração de variáveis de ambiente."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔍 VALIDAÇÃO DE CONFIGURAÇÃO{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Verificar se .env existe
    env_file = Path('.env')
    if not env_file.exists():
        print_status("Arquivo .env não encontrado!", "error")
        print_status("Execute: cp .env.example .env", "info")
        return False
    
    print_status("Arquivo .env encontrado", "success")
    
    # Carregar .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_status("Variáveis carregadas do .env", "success")
    except ImportError:
        print_status("python-dotenv não instalado", "error")
        print_status("Execute: pip install python-dotenv", "info")
        return False
    
    print()
    
    # Validar variáveis obrigatórias
    print(f"{BLUE}📋 Verificando variáveis obrigatórias...{RESET}\n")
    
    missing = []
    warnings = []
    valid_count = 0
    
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        
        if not value:
            missing.append(var)
            print_status(f"{var}: NÃO DEFINIDA", "error")
        else:
            # Verificar valores padrão perigosos
            if var in DEFAULT_VALUES_WARNING:
                if value == DEFAULT_VALUES_WARNING[var]:
                    warnings.append(f"{var} está com valor padrão inseguro!")
                    print_status(f"{var}: '{value}' (VALOR PADRÃO - ALTERE!)", "warning")
                else:
                    print_status(f"{var}: definida", "success")
                    valid_count += 1
            else:
                print_status(f"{var}: definida", "success")
                valid_count += 1
    
    print()
    
    # Validar variáveis opcionais
    print(f"{BLUE}📋 Verificando variáveis opcionais...{RESET}\n")
    
    optional_count = 0
    for var in OPTIONAL_VARS:
        value = os.getenv(var)
        if value:
            print_status(f"{var}: {value}", "info")
            optional_count += 1
        else:
            print_status(f"{var}: usando padrão", "info")
    
    print()
    
    # Validações específicas
    print(f"{BLUE}🔍 Validações específicas...{RESET}\n")
    
    # Validar TARGET_STATES
    target_states = os.getenv('TARGET_STATES', '')
    if target_states:
        states = [s.strip() for s in target_states.split(',')]
        valid_states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
                       'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
                       'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
        
        invalid_states = [s for s in states if s.upper() not in valid_states]
        
        if invalid_states:
            print_status(f"Estados inválidos: {', '.join(invalid_states)}", "error")
            missing.append('TARGET_STATES (valores inválidos)')
        else:
            print_status(f"TARGET_STATES: {len(states)} estado(s) válido(s)", "success")
    
    # Validar porta API
    api_port = os.getenv('API_PORT', '8000')
    try:
        port = int(api_port)
        if 1 <= port <= 65535:
            print_status(f"API_PORT: {port} (válida)", "success")
        else:
            print_status("API_PORT: fora do range 1-65535", "error")
            missing.append('API_PORT (valor inválido)')
    except ValueError:
        print_status("API_PORT: não é um número válido", "error")
        missing.append('API_PORT (não numérico)')
    
    # Validar LOG_LEVEL
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level.upper() in valid_levels:
        print_status(f"LOG_LEVEL: {log_level} (válido)", "success")
    else:
        print_status(f"LOG_LEVEL: {log_level} (inválido, use: {', '.join(valid_levels)})", "warning")
        warnings.append(f"LOG_LEVEL '{log_level}' não é padrão")
    
    print()
    
    # Resumo
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 RESUMO{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print(f"Variáveis obrigatórias: {valid_count}/{len(REQUIRED_VARS)}")
    print(f"Variáveis opcionais: {optional_count}/{len(OPTIONAL_VARS)}")
    
    if missing:
        print(f"\n{RED}❌ Variáveis faltando ou inválidas:{RESET}")
        for item in missing:
            print(f"   - {item}")
    
    if warnings:
        print(f"\n{YELLOW}⚠️ Avisos:{RESET}")
        for warn in warnings:
            print(f"   - {warn}")
    
    print()
    
    # Resultado final
    if missing:
        print_status("CONFIGURAÇÃO INVÁLIDA - Corrija os erros acima", "error")
        print()
        return False
    elif warnings:
        print_status("CONFIGURAÇÃO VÁLIDA - Mas há avisos de segurança", "warning")
        print_status("Recomendado: alterar valores padrão antes de produção", "info")
        print()
        return True
    else:
        print_status("CONFIGURAÇÃO VÁLIDA - Tudo OK! ✨", "success")
        print()
        return True


def main():
    """Entry point."""
    try:
        is_valid = validate_config()
        sys.exit(0 if is_valid else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️ Validação cancelada{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Erro inesperado: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
