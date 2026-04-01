"""ETL pipeline orchestrator for SNCR data extraction and loading."""
import asyncio
from typing import List
from decimal import Decimal
from datetime import datetime

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
from src.adapters.scraper import SNCRScraper
from src.adapters.repository import ImovelRepository


class ETLPipeline:
    """
    ETL Pipeline for extracting, transforming, and loading SNCR data.
    
    Orchestrates:
    - Data extraction from SNCR website
    - Data transformation and validation
    - Idempotent loading into PostgreSQL
    - Metadata logging for auditing
    """
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.repository: ImovelRepository = None
    
    async def initialize(self) -> None:
        """Initialize database connection."""
        await db.connect()
        self.repository = ImovelRepository(db)
        logger.info("ETL Pipeline initialized")
    
    async def shutdown(self) -> None:
        """Cleanup resources."""
        await db.disconnect()
        logger.info("ETL Pipeline shutdown")
    
    def transform_dataframe(self, df: pd.DataFrame, uf: str, municipio: str) -> List[ImovelCompleto]:
        """
        Transform raw DataFrame into domain models.
        
        Expected CSV columns:
        - codigo_incra: Property code
        - area_ha: Area in hectares
        - situacao: Status (Ativo, Inativo, etc.)
        - cpf: Owner/tenant CPF
        - nome_completo: Full name
        - tipo_vinculo: Relationship type (Proprietário, Arrendatário)
        - participacao_pct: Ownership percentage
        """
        imoveis_dict = {}
        
        for _, row in df.iterrows():
            try:
                codigo_incra = str(row.get("codigo_incra", "")).strip()
                
                if not codigo_incra or len(codigo_incra) != 17:
                    logger.warning(f"Invalid codigo_incra: {codigo_incra}")
                    continue
                
                # Create or get imovel
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
                
                # Add vinculo if present
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
                logger.error(f"Failed to transform row: {e}", row=row.to_dict())
                continue
        
        logger.info(f"Transformed {len(imoveis_dict)} properties from DataFrame")
        return list(imoveis_dict.values())
    
    async def load_dataframe(
        self, 
        df: pd.DataFrame, 
        uf: str, 
        municipio: str,
    ) -> ExtractionMetadata:
        """
        Load a DataFrame into the database.
        
        Returns metadata about the extraction.
        """
        metadata = ExtractionMetadata(
            uf=uf.upper(),
            municipio=municipio,
            total_registros=len(df),
            status="success",
        )
        
        try:
            # Transform data
            imoveis = self.transform_dataframe(df, uf, municipio)
            
            if not imoveis:
                logger.warning(f"No valid properties found for {municipio}/{uf}")
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
                f"Loaded {saved_count} properties for {municipio}/{uf}",
                saved=saved_count,
                total=len(imoveis),
            )
        
        except Exception as e:
            logger.error(f"Failed to load data for {municipio}/{uf}: {e}")
            metadata.status = "failed"
            metadata.erro_mensagem = str(e)
        
        finally:
            # Save metadata
            await self.repository.save_extraction_metadata(metadata)
        
        return metadata
    
    async def run_extraction(self, states: List[str] = None) -> None:
        """
        Run extraction for specified states.
        
        Args:
            states: List of state abbreviations. If None, uses configured states.
        """
        if states is None:
            states = self.settings.target_states_list
        
        logger.info(f"Starting extraction for states: {', '.join(states)}")
        
        await self.initialize()
        
        try:
            with SNCRScraper() as scraper:
                for uf in states:
                    logger.info(f"Processing state: {uf}")
                    
                    try:
                        # Extract data
                        dataframes = scraper.extract_state(uf)
                        
                        if not dataframes:
                            logger.warning(f"No data extracted for {uf}")
                            continue
                        
                        # Load each municipality's data
                        for df in dataframes:
                            if df.empty:
                                continue
                            
                            municipio = df["municipio"].iloc[0] if "municipio" in df.columns else "Unknown"
                            
                            await self.load_dataframe(df, uf, municipio)
                            
                            # Small delay between loads
                            await asyncio.sleep(0.5)
                    
                    except Exception as e:
                        logger.error(f"Failed to process state {uf}: {e}")
                        continue
            
            # Print statistics
            stats = await self.repository.get_statistics()
            logger.info("Extraction complete!", **stats)
        
        finally:
            await self.shutdown()


async def main() -> None:
    """Main entry point for ETL pipeline."""
    pipeline = ETLPipeline()
    await pipeline.run_extraction()


if __name__ == "__main__":
    asyncio.run(main())
