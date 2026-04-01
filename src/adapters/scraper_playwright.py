"""Playwright-based web scraper for SNCR data extraction with captcha solving."""
import re
import asyncio
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from loguru import logger

from src.infrastructure.config import get_settings


class SNCRPlaywrightScraper:
    """
    Browser automation scraper using Playwright for JavaScript-heavy sites.
    
    Features:
    - Automatic captcha solving (reads displayed text)
    - State and municipality selection
    - CSV file download management
    - Headless and visible browser modes
    - Robust error handling with timeouts
    """
    
    def __init__(self, headless: bool = True) -> None:
        """
        Initialize the Playwright scraper.
        
        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.settings = get_settings()
        self.base_url = self.settings.BASE_URL
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self) -> "SNCRPlaywrightScraper":
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def start(self) -> None:
        """Initialize Playwright and browser."""
        logger.info("Iniciando Playwright...")
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with anti-detection arguments
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ],
        )
        
        # Create page with realistic viewport
        self.page = await self.browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        
        # Remove webdriver flag
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        logger.info("✅ Navegador iniciado")
    
    async def close(self) -> None:
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
            logger.info("✅ Navegador fechado")
        
        if self.playwright:
            await self.playwright.stop()
    
    async def navegar_para_dados_abertos(self) -> bool:
        """
        Navigate to the main page and click 'Dados Abertos' link.
        
        Returns:
            True if navigation succeeded, False otherwise.
        """
        try:
            logger.info(f"Acessando {self.base_url}...")
            
            # Navigate to main page
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            logger.info("✅ Página carregada")
            
            # Click on "Dados Abertos" link
            logger.info("Clicando em 'Dados Abertos'...")
            await self.page.click('a[data-page="dados-abertos"]', timeout=10000)
            
            # Wait for page transition
            await self.page.wait_for_timeout(1000)
            
            logger.info("✅ Página 'Dados Abertos' acessada")
            return True
            
        except PlaywrightTimeout:
            logger.error("❌ Timeout ao navegar para 'Dados Abertos'")
            return False
        except Exception as e:
            logger.error(f"❌ Erro na navegação: {e}")
            return False
    
    async def resolver_captcha(self) -> bool:
        """
        Automatically solve the numeric captcha.
        
        The captcha displays digits with spaces (e.g., "1 2 8 1 0").
        This method reads the text, removes spaces, and fills the input.
        
        Returns:
            True if captcha solved successfully, False otherwise.
        """
        try:
            logger.info("Resolvendo captcha...")
            
            # Wait for captcha to be visible
            await self.page.wait_for_selector('#captcha-text-export', timeout=10000)
            
            # Read captcha text
            captcha_element = await self.page.query_selector('#captcha-text-export')
            captcha_text = await captcha_element.inner_text()
            
            # Remove spaces to get the actual number
            # Example: "1 2 8 1 0" → "12810"
            captcha_digits = re.sub(r'\s+', '', captcha_text)
            
            logger.info(f"📝 Captcha detectado: '{captcha_text}' → '{captcha_digits}'")
            
            # Fill captcha input
            await self.page.fill('#captcha-input-export', captcha_digits)
            
            # Wait for JavaScript validation
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
        Select a state from the dropdown.
        
        Args:
            uf: State abbreviation (e.g., 'SP', 'MG')
        
        Returns:
            True if selection succeeded, False otherwise.
        """
        try:
            logger.info(f"Selecionando estado: {uf}")
            
            # Wait for select to be enabled
            await self.page.wait_for_selector('#select-uf:not([disabled])', timeout=10000)
            
            # Select the state
            await self.page.select_option('#select-uf', value=uf.upper())
            
            # Wait for municipality dropdown to update
            await self.page.wait_for_timeout(500)
            
            logger.info(f"✅ Estado {uf} selecionado")
            return True
            
        except PlaywrightTimeout:
            logger.error("❌ Timeout ao selecionar estado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao selecionar estado: {e}")
            return False
    
    async def selecionar_municipio(self, municipio: Optional[str] = None) -> bool:
        """
        Select a municipality from the dropdown.
        
        Args:
            municipio: Municipality name (optional, None = all municipalities)
        
        Returns:
            True if selection succeeded, False otherwise.
        """
        try:
            if not municipio:
                logger.info("Mantendo 'Todos os municípios'")
                return True
            
            logger.info(f"Selecionando município: {municipio}")
            
            # Wait for select to be enabled
            await self.page.wait_for_selector('#select-municipio:not([disabled])', timeout=5000)
            
            # Select the municipality
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
        Click download button and save CSV file.
        
        Args:
            output_dir: Directory to save the CSV
        
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            logger.info("Iniciando download do CSV...")
            
            # Wait for button to be enabled
            await self.page.wait_for_selector('#btn-exportar:not([disabled])', timeout=10000)
            
            # Setup download
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Wait for download to start
            async with self.page.expect_download() as download_info:
                await self.page.click('#btn-exportar')
                logger.info("⏳ Aguardando download...")
            
            download = await download_info.value
            
            # Save file
            filename = download.suggested_filename
            filepath = output_path / filename
            await download.save_as(str(filepath))
            
            logger.info(f"✅ CSV baixado: {filepath}")
            return str(filepath)
            
        except PlaywrightTimeout:
            logger.error("❌ Timeout: Botão de download não foi habilitado")
            
            # Debug: check button state
            btn = await self.page.query_selector('#btn-exportar')
            if btn:
                is_disabled = await btn.get_attribute('disabled')
                logger.debug(f"Botão disabled: {is_disabled}")
            
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao baixar CSV: {e}")
            return None
    
    async def extrair_estado(
        self, 
        uf: str, 
        municipio: Optional[str] = None,
        output_dir: str = "data_download"
    ) -> Optional[str]:
        """
        Complete workflow: navigate, solve captcha, select state, download CSV.
        
        Args:
            uf: State abbreviation
            municipio: Municipality name (optional)
            output_dir: Base directory for downloads
        
        Returns:
            Path to downloaded CSV file or None if failed
        """
        logger.info(f"{'='*70}")
        logger.info(f"Extraindo dados: {uf}" + (f" - {municipio}" if municipio else ""))
        logger.info(f"{'='*70}")
        
        # 1. Navigate to Dados Abertos
        if not await self.navegar_para_dados_abertos():
            return None
        
        # 2. Solve captcha
        if not await self.resolver_captcha():
            return None
        
        # 3. Select state
        if not await self.selecionar_estado(uf):
            return None
        
        # 4. Select municipality (if specified)
        if not await self.selecionar_municipio(municipio):
            return None
        
        # 5. Download CSV
        state_output_dir = f"{output_dir}/{uf}"
        filepath = await self.baixar_csv(output_dir=state_output_dir)
        
        if filepath:
            logger.info(f"✅ Extração concluída: {filepath}")
        else:
            logger.error(f"❌ Falha na extração de {uf}")
        
        return filepath
    
    async def extrair_multiplos_estados(
        self, 
        estados: List[str],
        output_dir: str = "data_download"
    ) -> dict[str, Optional[str]]:
        """
        Extract data for multiple states sequentially.
        
        Args:
            estados: List of state abbreviations
            output_dir: Base directory for downloads
        
        Returns:
            Dictionary mapping state to downloaded file path
        """
        resultados = {}
        
        for uf in estados:
            try:
                filepath = await self.extrair_estado(uf, output_dir=output_dir)
                resultados[uf] = filepath
                
                # Small delay between states to avoid rate limiting
                if filepath:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"Erro ao processar {uf}: {e}")
                resultados[uf] = None
        
        return resultados
