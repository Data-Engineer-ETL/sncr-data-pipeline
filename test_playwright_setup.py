"""
Script de teste para validar a instalação e funcionamento do Playwright.
Execute: python test_playwright_setup.py
"""
import asyncio
import sys
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_step(step: str, message: str, status: str = "info"):
    """Print formatted step message."""
    colors = {
        "info": BLUE,
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
    }
    color = colors.get(status, RESET)
    print(f"{color}[{step}]{RESET} {message}")


async def test_playwright_import():
    """Test 1: Import Playwright module."""
    print_step("1/6", "Testando import do Playwright...", "info")
    try:
        from playwright.async_api import async_playwright
        print_step("1/6", "✅ Playwright importado com sucesso!", "success")
        return True
    except ImportError as e:
        print_step("1/6", f"❌ Erro ao importar: {e}", "error")
        print_step("FIX", "Execute: pip install playwright", "warning")
        return False


async def test_playwright_install():
    """Test 2: Check if Chromium is installed."""
    print_step("2/6", "Verificando instalação do Chromium...", "info")
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
        print_step("2/6", "✅ Chromium instalado e funcional!", "success")
        return True
    except Exception as e:
        print_step("2/6", f"❌ Erro: {e}", "error")
        print_step("FIX", "Execute: python -m playwright install chromium", "warning")
        return False


async def test_basic_navigation():
    """Test 3: Basic page navigation."""
    print_step("3/6", "Testando navegação básica...", "info")
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://example.com", timeout=10000)
            title = await page.title()
            await browser.close()
            
        print_step("3/6", f"✅ Página carregada: '{title}'", "success")
        return True
    except Exception as e:
        print_step("3/6", f"❌ Erro na navegação: {e}", "error")
        return False


async def test_scraper_import():
    """Test 4: Import project scraper."""
    print_step("4/6", "Testando import do SNCRPlaywrightScraper...", "info")
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from src.adapters.scraper_playwright import SNCRPlaywrightScraper
        print_step("4/6", "✅ Scraper importado com sucesso!", "success")
        return True
    except ImportError as e:
        print_step("4/6", f"❌ Erro ao importar: {e}", "error")
        print_step("FIX", "Verifique se src/adapters/scraper_playwright.py existe", "warning")
        return False


async def test_scraper_initialization():
    """Test 5: Initialize scraper."""
    print_step("5/6", "Testando inicialização do scraper...", "info")
    try:
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from src.adapters.scraper_playwright import SNCRPlaywrightScraper
        
        async with SNCRPlaywrightScraper(headless=True) as scraper:
            print_step("5/6", "✅ Scraper inicializado com sucesso!", "success")
        return True
    except Exception as e:
        print_step("5/6", f"❌ Erro na inicialização: {e}", "error")
        return False


async def test_download_directory():
    """Test 6: Check download directory."""
    print_step("6/6", "Verificando diretório de downloads...", "info")
    try:
        download_dir = Path("data_download")
        download_dir.mkdir(exist_ok=True)
        
        # Test write permission
        test_file = download_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        
        print_step("6/6", f"✅ Diretório OK: {download_dir.absolute()}", "success")
        return True
    except Exception as e:
        print_step("6/6", f"❌ Erro: {e}", "error")
        return False


async def main():
    """Run all tests."""
    print("=" * 70)
    print(f"{BLUE}🧪 TESTE DE CONFIGURAÇÃO PLAYWRIGHT{RESET}")
    print("=" * 70)
    print()
    
    tests = [
        test_playwright_import,
        test_playwright_install,
        test_basic_navigation,
        test_scraper_import,
        test_scraper_initialization,
        test_download_directory,
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()
    
    # Summary
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"{GREEN}✅ SUCESSO: Todos os testes passaram! ({passed}/{total}){RESET}")
        print()
        print(f"{GREEN}Você está pronto para rodar:{RESET}")
        print(f"{BLUE}  python scripts/run_etl_playwright.py --visible{RESET}")
    else:
        failed = total - passed
        print(f"{RED}❌ FALHA: {failed} teste(s) falharam ({passed}/{total} OK){RESET}")
        print()
        print(f"{YELLOW}Corrija os erros acima antes de continuar.{RESET}")
        sys.exit(1)
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
