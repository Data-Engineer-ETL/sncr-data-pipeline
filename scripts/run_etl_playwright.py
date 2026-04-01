"""ETL pipeline orchestrator using Playwright for extraction."""
import asyncio
from typing import List, Optional
from pathlib import Path
from decimal import Decimal

import pandas as pd
from loguru import logger

from src.domain.models import (
    Imovel,
    ImovelCompleto,
    VinculoPessoa,
    TipoVinculo,
    SituacaoImovel,
    ExtractionMetadata,
)
from src.infrastructure.database import db
from src.infrastructure.config import get_settings
from src.adapters.scraper_playwright import SNCRPlaywrightScraper
from src.adapters.repository import ImovelRepository


class PlaywrightETLPipeline:
    """
    ETL Pipeline using Playwright for data extraction.
    
    Workflow:
    1. Use Playwright to navigate site and download CSVs
    2. Read CSV files from disk
    3. Transform data into domain models
    4. Load into PostgreSQL with idempotency
    5. Log metadata for auditing
    """
    
    def __init__(self, headless: bool = True) -> None:
        """
        Initialize ETL pipeline.
        
        Args:
            headless: Run browser in headless mode
        """
        self.settings = get_settings()
        self.headless = headless
        self.repository: ImovelRepository = None
        self.download_dir = Path("data_download")
    
    async def initialize(self) -> None:
        """Initialize database connection."""
        await db.connect()
        self.repository = ImovelRepository(db)
        logger.info("🚀 ETL Pipeline inicializado (modo Playwright)")
    
    async def shutdown(self) -> None:
        """Cleanup resources."""
        await db.disconnect()
        logger.info("👋 ETL Pipeline finalizado")
    
    def transform_dataframe(
        self, 
        df: pd.DataFrame, 
        uf: str, 
        municipio: str
    ) -> List[ImovelCompleto]:
        """
        Transform raw DataFrame into domain models.
        
        Expected CSV columns:
        - codigo_incra: Property code (17 digits)
        - area_ha: Area in hectares
        - situacao: Status (Ativo, Inativo, etc.)
        - cpf: Owner/tenant CPF (11 digits)
        - nome_completo: Full name
        - tipo_vinculo: Relationship type (Proprietário, Arrendatário)
        - participacao_pct: Ownership percentage
        """
        imoveis_dict = {}
        
        for _, row in df.iterrows():
            try:
                codigo_incra = str(row.get("codigo_incra", "")).strip()
                
                if not codigo_incra or len(codigo_incra) != 17:
                    logger.warning(f"Código INCRA inválido: {codigo_incra}")
                    continue
                
                # Create or get property
                if codigo_incra not in imoveis_dict:
                    imovel = Imovel(
                        codigo_incra=codigo_incra,
                        area_ha=Decimal(str(row.get("area_ha", 0))),
                        situacao=SituacaoImovel(row.get("situacao", "Ativo")),
                        municipio=municipio,
                        uf=uf.upper(),
                    )
                    
                    imoveis_dict[codigo_incra] = ImovelCompleto(
                        imovel=imovel,
                        vinculos=[],
                    )
                
                # Add person relationship if present
                cpf = str(row.get("cpf", "")).strip()
                nome = str(row.get("nome_completo", "")).strip()
                
                if cpf and nome:
                    # Clean CPF (remove formatting)
                    cpf_clean = "".join(filter(str.isdigit, cpf))
                    
                    if len(cpf_clean) == 11:
                        vinculo = VinculoPessoa(
                            cpf=cpf_clean,
                            nome_completo=nome,
                            vinculo=TipoVinculo(row.get("tipo_vinculo", "Proprietário")),
                            participacao_pct=Decimal(str(row.get("participacao_pct", 100.0))),
                        )
                        
                        imoveis_dict[codigo_incra].vinculos.append(vinculo)
            
            except Exception as e:
                logger.error(f"Erro ao transformar linha: {e}", row=row.to_dict())
                continue
        
        logger.info(f"✅ Transformados {len(imoveis_dict)} imóveis")
        return list(imoveis_dict.values())
    
    async def load_csv_file(
        self, 
        csv_path: str, 
        uf: str, 
        municipio: str = "Todos"
    ) -> ExtractionMetadata:
        """
        Load a CSV file into the database.
        
        Args:
            csv_path: Path to CSV file
            uf: State abbreviation
            municipio: Municipality name
        
        Returns:
            Metadata about the extraction
        """
        metadata = ExtractionMetadata(
            uf=uf.upper(),
            municipio=municipio,
            total_registros=0,
            status="success",
        )
        
        try:
            # Read CSV
            logger.info(f"📖 Lendo CSV: {csv_path}")
            df = pd.read_csv(csv_path)
            
            if df.empty:
                logger.warning(f"CSV vazio: {csv_path}")
                metadata.status = "partial"
                metadata.erro_mensagem = "CSV file is empty"
                return metadata
            
            logger.info(f"📊 CSV contém {len(df)} registros")
            
            # Transform data
            imoveis = self.transform_dataframe(df, uf, municipio)
            
            if not imoveis:
                logger.warning(f"Nenhum imóvel válido encontrado em {csv_path}")
                metadata.status = "partial"
                metadata.erro_mensagem = "No valid properties after transformation"
                return metadata
            
            # Load into database
            saved_count = await self.repository.bulk_save_imoveis(imoveis)
            
            metadata.total_registros = saved_count
            
            if saved_count < len(imoveis):
                metadata.status = "partial"
                metadata.erro_mensagem = f"Saved {saved_count}/{len(imoveis)} properties"
            
            logger.info(
                f"💾 Carregados {saved_count} imóveis para {municipio}/{uf}",
                saved=saved_count,
                total=len(imoveis),
            )
        
        except FileNotFoundError:
            logger.error(f"❌ Arquivo não encontrado: {csv_path}")
            metadata.status = "failed"
            metadata.erro_mensagem = f"File not found: {csv_path}"
        
        except Exception as e:
            logger.error(f"❌ Erro ao carregar CSV {csv_path}: {e}")
            metadata.status = "failed"
            metadata.erro_mensagem = str(e)
        
        finally:
            # Save metadata
            await self.repository.save_extraction_metadata(metadata)
        
        return metadata
    
    async def run_extraction(
        self, 
        states: Optional[List[str]] = None,
        skip_download: bool = False
    ) -> None:
        """
        Run extraction for specified states using Playwright.
        
        Args:
            states: List of state abbreviations. If None, uses configured states.
            skip_download: If True, skip download and only load existing CSVs
        """
        if states is None:
            states = self.settings.target_states_list
        
        logger.info(f"🎯 Iniciando extração para estados: {', '.join(states)}")
        
        await self.initialize()
        
        try:
            # Phase 1: Download CSVs using Playwright
            if not skip_download:
                logger.info("📥 FASE 1: Download de CSVs com Playwright")
                logger.info("=" * 70)
                
                async with SNCRPlaywrightScraper(headless=self.headless) as scraper:
                    resultados = await scraper.extrair_multiplos_estados(
                        estados=states,
                        output_dir=str(self.download_dir)
                    )
                    
                    # Log results
                    for uf, filepath in resultados.items():
                        if filepath:
                            logger.info(f"✅ {uf}: {filepath}")
                        else:
                            logger.error(f"❌ {uf}: Falha no download")
            else:
                logger.info("⏭️ Pulando download (skip_download=True)")
            
            # Phase 2: Load CSVs into database
            logger.info("")
            logger.info("📊 FASE 2: Carga no banco de dados")
            logger.info("=" * 70)
            
            for uf in states:
                try:
                    # Find CSV file for this state
                    csv_path = self.download_dir / uf / f"SNCR_{uf}.csv"
                    
                    if not csv_path.exists():
                        logger.warning(f"⚠️ CSV não encontrado para {uf}: {csv_path}")
                        continue
                    
                    # Load CSV into database
                    await self.load_csv_file(
                        csv_path=str(csv_path),
                        uf=uf,
                        municipio="Todos"
                    )
                    
                    # Small delay between loads
                    await asyncio.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar estado {uf}: {e}")
                    continue
            
            # Phase 3: Print statistics
            logger.info("")
            logger.info("📈 ESTATÍSTICAS FINAIS")
            logger.info("=" * 70)
            
            stats = await self.repository.get_statistics()
            
            logger.info(f"🏠 Total de imóveis: {stats.get('total_imoveis', 0)}")
            logger.info(f"👥 Total de pessoas: {stats.get('total_pessoas', 0)}")
            logger.info(f"🔗 Total de vínculos: {stats.get('total_vinculos', 0)}")
            logger.info(f"🗺️ Estados processados: {stats.get('total_estados', 0)}")
            logger.info(f"🏘️ Municípios processados: {stats.get('total_municipios', 0)}")
            
            logger.info("")
            logger.info("✅ Extração concluída com sucesso!")
        
        finally:
            await self.shutdown()


async def main(
    states: Optional[List[str]] = None,
    headless: bool = True,
    skip_download: bool = False
) -> None:
    """
    Main entry point for Playwright ETL pipeline.
    
    Args:
        states: List of states to extract (e.g., ['SP', 'MG', 'RJ'])
        headless: Run browser in headless mode
        skip_download: Skip download phase and only load existing CSVs
    """
    pipeline = PlaywrightETLPipeline(headless=headless)
    await pipeline.run_extraction(states=states, skip_download=skip_download)


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    states = None
    headless = True
    skip_download = False
    
    if "--visible" in args:
        headless = False
        args.remove("--visible")
    
    if "--skip-download" in args:
        skip_download = True
        args.remove("--skip-download")
    
    if args:
        states = args
    
    # Run pipeline
    asyncio.run(main(states=states, headless=headless, skip_download=skip_download))
