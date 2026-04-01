"""
Seed script to populate database with sample data for testing.

Usage:
    python scripts/seed_db.py
"""
import asyncio
from decimal import Decimal
from loguru import logger

from src.domain.models import Imovel, ImovelCompleto, VinculoPessoa, TipoVinculo, SituacaoImovel
from src.infrastructure.database import db
from src.adapters.repository import ImovelRepository


SAMPLE_DATA = [
    {
        "imovel": {
            "codigo_incra": "12345678901234567",
            "area_ha": Decimal("142.50"),
            "situacao": SituacaoImovel.ATIVO,
            "municipio": "Campinas",
            "uf": "SP",
        },
        "vinculos": [
            {
                "cpf": "12345678972",
                "nome_completo": "Maria Aparecida de Souza",
                "vinculo": TipoVinculo.PROPRIETARIO,
                "participacao_pct": Decimal("100.0"),
            }
        ],
    },
    {
        "imovel": {
            "codigo_incra": "98765432109876543",
            "area_ha": Decimal("85.75"),
            "situacao": SituacaoImovel.ATIVO,
            "municipio": "Santos",
            "uf": "SP",
        },
        "vinculos": [
            {
                "cpf": "98765432109",
                "nome_completo": "João Pedro Silva",
                "vinculo": TipoVinculo.PROPRIETARIO,
                "participacao_pct": Decimal("60.0"),
            },
            {
                "cpf": "11122233344",
                "nome_completo": "Ana Paula Costa",
                "vinculo": TipoVinculo.PROPRIETARIO,
                "participacao_pct": Decimal("40.0"),
            },
        ],
    },
    {
        "imovel": {
            "codigo_incra": "55566677788899900",
            "area_ha": Decimal("320.00"),
            "situacao": SituacaoImovel.ATIVO,
            "municipio": "Ribeirão Preto",
            "uf": "SP",
        },
        "vinculos": [
            {
                "cpf": "55566677788",
                "nome_completo": "Carlos Eduardo Oliveira",
                "vinculo": TipoVinculo.PROPRIETARIO,
                "participacao_pct": Decimal("100.0"),
            }
        ],
    },
    {
        "imovel": {
            "codigo_incra": "11223344556677889",
            "area_ha": Decimal("450.25"),
            "situacao": SituacaoImovel.ATIVO,
            "municipio": "Belo Horizonte",
            "uf": "MG",
        },
        "vinculos": [
            {
                "cpf": "11223344556",
                "nome_completo": "Fernanda Rodrigues Lima",
                "vinculo": TipoVinculo.PROPRIETARIO,
                "participacao_pct": Decimal("80.0"),
            },
            {
                "cpf": "66677788899",
                "nome_completo": "Roberto Santos Alves",
                "vinculo": TipoVinculo.ARRENDATARIO,
                "participacao_pct": Decimal("20.0"),
            },
        ],
    },
    {
        "imovel": {
            "codigo_incra": "99988877766655544",
            "area_ha": Decimal("210.80"),
            "situacao": SituacaoImovel.ATIVO,
            "municipio": "Rio de Janeiro",
            "uf": "RJ",
        },
        "vinculos": [
            {
                "cpf": "99988877766",
                "nome_completo": "Patricia Mendes Ferreira",
                "vinculo": TipoVinculo.PROPRIETARIO,
                "participacao_pct": Decimal("100.0"),
            }
        ],
    },
]


async def seed_database() -> None:
    """Seed database with sample data."""
    logger.info("=== Database Seeding ===")
    
    await db.connect()
    repository = ImovelRepository(db)
    
    try:
        saved_count = 0
        
        for data in SAMPLE_DATA:
            # Create domain models
            imovel = Imovel(**data["imovel"])
            vinculos = [VinculoPessoa(**v) for v in data["vinculos"]]
            
            imovel_completo = ImovelCompleto(
                imovel=imovel,
                vinculos=vinculos,
            )
            
            # Save to database
            await repository.save_imovel_completo(imovel_completo)
            saved_count += 1
            
            logger.info(
                f"Saved: {imovel.codigo_incra} - {imovel.municipio}/{imovel.uf}",
                vinculos=len(vinculos),
            )
        
        # Get statistics
        stats = await repository.get_statistics()
        
        logger.info("✅ Seeding complete!", saved=saved_count, **stats)
    
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise
    
    finally:
        await db.disconnect()


async def main() -> None:
    """Main entry point."""
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
