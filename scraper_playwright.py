"""
Automação do SNCR usando Playwright para baixar CSVs.

Este script navega pela página web do SNCR, resolve o captcha automaticamente,
seleciona estados e municípios, e baixa os arquivos CSV.

Requisitos:
    pip install playwright
    python -m playwright install chromium

Usage:
    python scraper_playwright.py
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional
import re

# Adiciona o projeto ao path
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from loguru import logger

from src.infrastructure.config import get_settings


class SNCRPlaywrightScraper:
    """Scraper usando Playwright para navegação real no site SNCR."""
    
    def __init__(self, headless: bool = False):
        """
        Inicializa o scraper.
        
        Args:
            headless: Se True, executa sem interface gráfica (mais rápido).
                     Se False, mostra o navegador (útil para debug).
        """
        self.settings = get_settings()
        self.base_url = self.settings.BASE_URL
        self.headless = headless
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
    
    async def start(self):
        """Inicia o navegador."""
        logger.info("Iniciando Playwright...")
        self.playwright = await async_playwright().start()
        
        # Inicia navegador Chromium
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']  # Anti-detecção
        )
        
        # Cria contexto (similar a uma sessão)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Cria página
        self.page = await self.context.new_page()
        
        logger.info("Navegador iniciado")
    
    async def close(self):
        """Fecha o navegador."""
        if self.page:
            await self.page.close()
        if hasattr(self, 'context'):
            await self.context.close()
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        logger.info("Navegador fechado")
    
    async def navegar_para_dados_abertos(self):
        """Navega para a página inicial e clica em 'Dados Abertos'."""
        logger.info(f"Acessando {self.base_url}...")
        
        try:
            # Acessa a página
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            logger.info("Página carregada")
            
            # Aguarda um pouco para garantir que JavaScript carregou
            await self.page.wait_for_timeout(1000)
            
            # Clica no link "Dados Abertos"
            # Pode ser que já esteja na página, então verifica primeiro
            dados_abertos_section = await self.page.query_selector('#page-dados-abertos')
            
            if dados_abertos_section:
                # Verifica se já está visível
                is_visible = await dados_abertos_section.is_visible()
                
                if not is_visible:
                    logger.info("Clicando em 'Dados Abertos'...")
                    await self.page.click('a[data-page="dados-abertos"]')
                    await self.page.wait_for_timeout(500)
                else:
                    logger.info("Já está na página 'Dados Abertos'")
            
            logger.info("Página 'Dados Abertos' acessada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao navegar: {e}")
            return False
    
    async def resolver_captcha(self) -> bool:
        """
        Resolve o captcha automaticamente lendo o texto exibido.
        
        Returns:
            True se resolveu com sucesso, False caso contrário.
        """
        try:
            logger.info("Resolvendo captcha...")
            
            # Aguarda captcha aparecer
            await self.page.wait_for_selector('#captcha-text-export', timeout=5000)
            
            # Lê o texto do captcha
            captcha_element = await self.page.query_selector('#captcha-text-export')
            captcha_text = await captcha_element.inner_text()
            
            # Remove espaços e pega apenas os dígitos
            captcha_digits = re.sub(r'\s+', '', captcha_text)
            
            logger.info(f"📝 Captcha detectado: '{captcha_text}' → '{captcha_digits}'")
            
            # Verifica se tem 5 dígitos
            if len(captcha_digits) != 5 or not captcha_digits.isdigit():
                logger.error(f"❌ Captcha inválido: '{captcha_digits}'")
                return False
            
            # Preenche o input do captcha
            await self.page.fill('#captcha-input-export', captcha_digits)
            
            # Aguarda um pouco para o JavaScript validar
            await self.page.wait_for_timeout(500)
            
            logger.info("✅ Captcha resolvido")
            return True
            
        except PlaywrightTimeout:
            logger.error("❌ Timeout ao esperar captcha")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao resolver captcha: {e}")
            return False
    
    async def selecionar_estado(self, uf: str) -> bool:
        """
        Seleciona um estado no dropdown.
        
        Args:
            uf: Sigla do estado (ex: 'SP', 'MG')
        
        Returns:
            True se selecionou com sucesso, False caso contrário.
        """
        try:
            logger.info(f"Selecionando estado: {uf}")
            
            # Seleciona o estado no dropdown
            await self.page.select_option('#select-uf', value=uf.upper())
            
            # Aguarda um pouco para carregar municípios (se houver)
            await self.page.wait_for_timeout(1000)
            
            logger.info(f"✅ Estado {uf} selecionado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao selecionar estado: {e}")
            return False
    
    async def selecionar_municipio(self, municipio: Optional[str] = None) -> bool:
        """
        Seleciona um município (opcional).
        
        Args:
            municipio: Nome do município ou None para "Todos"
        
        Returns:
            True se selecionou com sucesso, False caso contrário.
        """
        try:
            if not municipio:
                logger.info("Mantendo 'Todos os municípios'")
                return True
            
            logger.info(f"Selecionando município: {municipio}")
            
            # Aguarda o select estar habilitado
            await self.page.wait_for_selector('#select-municipio:not([disabled])', timeout=5000)
            
            # Seleciona o município
            await self.page.select_option('#select-municipio', label=municipio)
            
            await self.page.wait_for_timeout(500)
            
            logger.info(f"✅ Município {municipio} selecionado")
            return True
            
        except PlaywrightTimeout:
            logger.warning("⚠️ Dropdown de município não foi habilitado (pode não ter municípios)")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao selecionar município: {e}")
            return False
    
    async def baixar_csv(self, output_dir: str = "data_download") -> Optional[str]:
        """
        Clica no botão de download e salva o CSV.
        
        Args:
            output_dir: Diretório onde salvar o CSV
        
        Returns:
            Caminho do arquivo baixado ou None se falhou
        """
        try:
            logger.info("Iniciando download do CSV...")
            
            # Aguarda botão estar habilitado
            await self.page.wait_for_selector('#btn-exportar:not([disabled])', timeout=10000)
            
            # Configura o download
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Aguarda o download começar
            async with self.page.expect_download() as download_info:
                # Clica no botão
                await self.page.click('#btn-exportar')
                logger.info("⏳ Aguardando download...")
            
            download = await download_info.value
            
            # Salva o arquivo
            filename = download.suggested_filename
            filepath = output_path / filename
            await download.save_as(str(filepath))
            
            logger.info(f"✅ CSV baixado: {filepath}")
            return str(filepath)
            
        except PlaywrightTimeout:
            logger.error("❌ Timeout: Botão de download não foi habilitado")
            
            # Debug: verifica estado do botão
            btn = await self.page.query_selector('#btn-exportar')
            if btn:
                is_disabled = await btn.get_attribute('disabled')
                logger.debug(f"Botão disabled: {is_disabled}")
            
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao baixar CSV: {e}")
            return None
    
    async def extrair_estado(self, uf: str, municipio: Optional[str] = None) -> Optional[str]:
        """
        Fluxo completo: navega, resolve captcha, seleciona estado e baixa CSV.
        
        Args:
            uf: Sigla do estado
            municipio: Nome do município (opcional)
        
        Returns:
            Caminho do arquivo baixado ou None se falhou
        """
        logger.info(f"{'='*70}")
        logger.info(f"Extraindo dados: {uf}" + (f" - {municipio}" if municipio else ""))
        logger.info(f"{'='*70}")
        
        # 1. Navegar para Dados Abertos
        if not await self.navegar_para_dados_abertos():
            return None
        
        # 2. Resolver captcha
        if not await self.resolver_captcha():
            return None
        
        # 3. Selecionar estado
        if not await self.selecionar_estado(uf):
            return None
        
        # 4. Selecionar município (se especificado)
        if not await self.selecionar_municipio(municipio):
            return None
        
        # 5. Baixar CSV
        filepath = await self.baixar_csv(output_dir=f"data_download/{uf}")
        
        if filepath:
            logger.info(f"✅ Extração concluída: {filepath}")
        else:
            logger.error(f"❌ Falha na extração de {uf}")
        
        return filepath


async def demo():
    """Demonstração do scraper Playwright."""
    print("=" * 70)
    print("🤖 AUTOMAÇÃO PLAYWRIGHT - SNCR")
    print("=" * 70)
    print()
    print("Este script usa Playwright para:")
    print("  1. Navegar pela página do SNCR")
    print("  2. Clicar em 'Dados Abertos'")
    print("  3. Resolver o captcha automaticamente")
    print("  4. Selecionar estado")
    print("  5. Baixar o CSV")
    print()
    print("💡 Dica: Você verá o navegador abrindo e executando as ações!")
    print("=" * 70)
    print()
    
    # Pergunta se quer rodar com/sem interface
    print("Modo de execução:")
    print("  [1] Com interface (você vê o navegador)")
    print("  [2] Sem interface (mais rápido, em background)")
    
    escolha = input("\nEscolha (1 ou 2): ").strip()
    headless = escolha == "2"
    
    if headless:
        print("\n🚀 Executando em modo headless (background)...\n")
    else:
        print("\n🌐 Abrindo navegador (você verá a automação acontecendo)...\n")
    
    # Estados para testar
    estados = ['SP']  # Você pode adicionar mais: ['SP', 'MG', 'RJ']
    
    try:
        async with SNCRPlaywrightScraper(headless=headless) as scraper:
            for uf in estados:
                # Extrai dados do estado (todos os municípios)
                filepath = await scraper.extrair_estado(uf)
                
                if filepath:
                    print(f"\n✅ Sucesso! Arquivo salvo em: {filepath}")
                else:
                    print(f"\n❌ Falha ao extrair {uf}")
                
                # Aguarda um pouco entre estados
                await asyncio.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Automação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        logger.exception("Erro na automação")
    
    print("\n" + "=" * 70)
    print("✅ AUTOMAÇÃO CONCLUÍDA")
    print("=" * 70)
    print()
    print(f"📁 Arquivos salvos em: ./data_download/")
    print()


if __name__ == "__main__":
    # Configura logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<dim>{time:HH:mm:ss}</dim> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Executa
    asyncio.run(demo())
