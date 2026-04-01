"""Web scraper for SNCR data extraction."""
import time
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from io import StringIO

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from loguru import logger

from src.infrastructure.config import get_settings
from src.infrastructure.checkpoint import CheckpointManager


class SNCRScraper:
    """
    Robust scraper for SNCR data with retry logic and checkpoint management.
    
    Features:
    - Exponential backoff for retries
    - Anti-bot detection and handling
    - Session management with cookies
    - CSV download and parsing
    - Checkpoint-based recovery
    """
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.BASE_URL
        self.checkpoint_manager = CheckpointManager(self.settings.CHECKPOINT_DIR)
        
        # HTTP client with reasonable defaults
        self.client = httpx.Client(
            timeout=self.settings.REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
        )
        
        self.session_initialized = False
    
    def __enter__(self) -> "SNCRScraper":
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
    
    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=1, max=30),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, "WARNING"),
    )
    def _make_request(self, url: str, method: str = "GET", **kwargs: Any) -> httpx.Response:
        """
        Make HTTP request with retry logic.
        
        Retries on network errors with exponential backoff.
        """
        logger.debug(f"Making {method} request to {url}")
        
        if method == "GET":
            response = self.client.get(url, **kwargs)
        elif method == "POST":
            response = self.client.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        
        # Check for anti-bot challenge
        if self._is_bot_challenge(response):
            logger.warning("Bot challenge detected, waiting before retry...")
            time.sleep(5)
            raise httpx.HTTPError("Bot challenge detected")
        
        return response
    
    def _is_bot_challenge(self, response: httpx.Response) -> bool:
        """
        Detect if response is an anti-bot challenge page.
        
        Common indicators:
        - JavaScript challenge page
        - Cloudflare challenge
        - reCAPTCHA
        """
        content = response.text.lower()
        
        # Check for common bot detection patterns
        bot_patterns = [
            "checking your browser",
            "enable javascript",
            "cloudflare",
            "captcha",
            "you have been blocked",
            "access denied",
        ]
        
        return any(pattern in content for pattern in bot_patterns)
    
    def initialize_session(self) -> None:
        """
        Initialize session by visiting the home page.
        
        This ensures cookies/sessions are properly set up.
        """
        if self.session_initialized:
            return
        
        try:
            logger.info("Initializing session with SNCR website")
            response = self._make_request(self.base_url)
            
            if response.status_code == 200:
                self.session_initialized = True
                logger.info("Session initialized successfully")
            else:
                logger.warning(f"Unexpected status code: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            raise
    
    def get_states(self) -> List[str]:
        """
        Get list of available states.
        
        In practice, we use configured states from settings.
        """
        return self.settings.target_states_list
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, "WARNING"),
    )
    def get_municipios(self, uf: str) -> List[str]:
        """
        Get list of municipalities for a state.
        
        Args:
            uf: State abbreviation (e.g., 'SP', 'MG')
        
        Returns:
            List of municipality names
        """
        logger.info(f"Fetching municipalities for {uf}")
        
        try:
            # Try to access the export page for the state
            url = f"{self.base_url}/export"
            response = self._make_request(url)
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for municipality select dropdown
            municipio_select = soup.find("select", {"name": "municipio"})
            
            if not municipio_select:
                # Fallback: use a predefined list or API endpoint
                logger.warning(f"Could not find municipality dropdown for {uf}")
                return self._get_fallback_municipios(uf)
            
            # Extract options
            municipios = []
            for option in municipio_select.find_all("option"):
                value = option.get("value")
                if value and value.strip():
                    municipios.append(value.strip())
            
            logger.info(f"Found {len(municipios)} municipalities for {uf}")
            return municipios
        
        except Exception as e:
            logger.error(f"Failed to fetch municipalities for {uf}: {e}")
            return self._get_fallback_municipios(uf)
    
    def _get_fallback_municipios(self, uf: str) -> List[str]:
        """
        Fallback method to get municipalities.
        
        In a real scenario, this would query a local database or API.
        For this challenge, we'll use some common municipalities.
        """
        # Sample municipalities for each state (expand as needed)
        fallback = {
            "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "Sorocaba"],
            "MG": ["Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim"],
            "RJ": ["Rio de Janeiro", "Niterói", "Duque de Caxias", "Nova Iguaçu", "Campos"],
        }
        
        return fallback.get(uf.upper(), [])
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        before_sleep=before_sleep_log(logger, "WARNING"),
    )
    def download_csv(self, uf: str, municipio: str) -> Optional[pd.DataFrame]:
        """
        Download CSV data for a municipality.
        
        Args:
            uf: State abbreviation
            municipio: Municipality name
        
        Returns:
            DataFrame with property data, or None if failed/empty
        """
        logger.info(f"Downloading data for {municipio}/{uf}")
        
        try:
            # Build export URL
            url = f"{self.base_url}/export"
            
            # POST request to export CSV
            data = {
                "uf": uf.upper(),
                "municipio": municipio,
                "format": "csv",
            }
            
            response = self._make_request(url, method="POST", data=data)
            
            # Check if we got CSV content
            content_type = response.headers.get("content-type", "")
            
            if "text/csv" not in content_type and "application/csv" not in content_type:
                logger.warning(f"Unexpected content type: {content_type}")
                # Try to parse anyway
            
            # Parse CSV
            csv_content = response.text
            
            if not csv_content or len(csv_content.strip()) < 10:
                logger.warning(f"Empty or invalid CSV for {municipio}/{uf}")
                return None
            
            # Read into DataFrame
            df = pd.read_csv(StringIO(csv_content))
            
            if df.empty:
                logger.info(f"No properties found for {municipio}/{uf}")
                return None
            
            logger.info(f"Downloaded {len(df)} records for {municipio}/{uf}")
            return df
        
        except Exception as e:
            logger.error(f"Failed to download CSV for {municipio}/{uf}: {e}")
            raise
    
    def extract_state(self, uf: str) -> List[pd.DataFrame]:
        """
        Extract all data for a state, respecting checkpoints.
        
        Args:
            uf: State abbreviation
        
        Returns:
            List of DataFrames (one per municipality)
        """
        logger.info(f"Starting extraction for state {uf}")
        
        # Initialize session
        self.initialize_session()
        
        # Get municipalities
        municipios = self.get_municipios(uf)
        
        if not municipios:
            logger.warning(f"No municipalities found for {uf}")
            return []
        
        # Load checkpoint
        processed = self.checkpoint_manager.load_checkpoint(uf)
        pending = [m for m in municipios if m not in processed]
        
        logger.info(
            f"Progress for {uf}: {len(processed)}/{len(municipios)} municipalities processed"
        )
        
        if not pending:
            logger.info(f"All municipalities already processed for {uf}")
            return []
        
        # Process pending municipalities
        results = []
        
        for i, municipio in enumerate(pending, 1):
            logger.info(f"Processing {municipio} ({i}/{len(pending)})")
            
            try:
                df = self.download_csv(uf, municipio)
                
                if df is not None and not df.empty:
                    # Add metadata columns
                    df["uf"] = uf.upper()
                    df["municipio"] = municipio
                    results.append(df)
                
                # Mark as processed
                self.checkpoint_manager.add_processed_municipio(uf, municipio)
                
                # Be nice to the server
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"Failed to process {municipio}/{uf}: {e}")
                # Continue with next municipality
                continue
        
        logger.info(f"Extraction complete for {uf}: {len(results)} municipalities with data")
        return results
    
    @staticmethod
    def calculate_file_hash(content: str) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(content.encode()).hexdigest()
