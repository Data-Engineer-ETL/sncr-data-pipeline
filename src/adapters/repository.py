"""Repository for property (imovel) data operations."""
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

import asyncpg
from loguru import logger

from src.domain.models import Imovel, ImovelCompleto, VinculoPessoa, ExtractionMetadata
from src.infrastructure.database import Database


class ImovelRepository:
    """
    Repository for managing property data with idempotent operations.
    
    Ensures data consistency through:
    - Upsert operations (INSERT ... ON CONFLICT)
    - Transaction management
    - Deduplication by natural keys
    """
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def upsert_imovel(self, imovel: Imovel, conn: asyncpg.Connection) -> int:
        """
        Insert or update an imovel record.
        
        Returns the internal ID of the imovel.
        
        This is idempotent: running multiple times with the same codigo_incra
        will update the existing record rather than creating duplicates.
        """
        query = """
            INSERT INTO imoveis (
                codigo_incra, area_ha, situacao, municipio, uf
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (codigo_incra) 
            DO UPDATE SET
                area_ha = EXCLUDED.area_ha,
                situacao = EXCLUDED.situacao,
                municipio = EXCLUDED.municipio,
                uf = EXCLUDED.uf,
                updated_at = NOW()
            RETURNING id
        """
        
        try:
            imovel_id = await conn.fetchval(
                query,
                imovel.codigo_incra,
                imovel.area_ha,
                imovel.situacao.value,
                imovel.municipio,
                imovel.uf,
            )
            
            logger.debug(f"Upserted imovel {imovel.codigo_incra} with ID {imovel_id}")
            return imovel_id
        
        except Exception as e:
            logger.error(f"Failed to upsert imovel {imovel.codigo_incra}: {e}")
            raise
    
    async def upsert_pessoa(self, cpf: str, nome_completo: str, conn: asyncpg.Connection) -> int:
        """
        Insert or update a pessoa record.
        
        Returns the internal ID of the pessoa.
        
        Idempotent: same CPF will return existing ID.
        """
        query = """
            INSERT INTO pessoas (cpf, nome_completo)
            VALUES ($1, $2)
            ON CONFLICT (cpf)
            DO UPDATE SET
                nome_completo = EXCLUDED.nome_completo,
                updated_at = NOW()
            RETURNING id
        """
        
        try:
            pessoa_id = await conn.fetchval(query, cpf, nome_completo)
            logger.debug(f"Upserted pessoa CPF {cpf} with ID {pessoa_id}")
            return pessoa_id
        
        except Exception as e:
            logger.error(f"Failed to upsert pessoa {cpf}: {e}")
            raise
    
    async def upsert_vinculo(
        self,
        imovel_id: int,
        pessoa_id: int,
        vinculo: VinculoPessoa,
        conn: asyncpg.Connection,
    ) -> int:
        """
        Insert or update a vinculo (relationship) record.
        
        Returns the internal ID of the vinculo.
        
        Idempotent: same imovel+pessoa+tipo will update existing record.
        """
        query = """
            INSERT INTO vinculos (imovel_id, pessoa_id, tipo_vinculo, participacao_pct)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (imovel_id, pessoa_id, tipo_vinculo)
            DO UPDATE SET
                participacao_pct = EXCLUDED.participacao_pct
            RETURNING id
        """
        
        try:
            vinculo_id = await conn.fetchval(
                query,
                imovel_id,
                pessoa_id,
                vinculo.vinculo.value,
                vinculo.participacao_pct,
            )
            
            logger.debug(f"Upserted vinculo ID {vinculo_id}")
            return vinculo_id
        
        except Exception as e:
            logger.error(f"Failed to upsert vinculo: {e}")
            raise
    
    async def save_imovel_completo(self, imovel_completo: ImovelCompleto) -> None:
        """
        Save a complete property record with all relationships.
        
        This operation is:
        - Atomic: all or nothing through transaction
        - Idempotent: safe to run multiple times
        - Resilient: handles partial failures gracefully
        """
        async with self.db.transaction() as conn:
            try:
                # 1. Upsert imovel
                imovel_id = await self.upsert_imovel(imovel_completo.imovel, conn)
                
                # 2. Upsert each pessoa and vinculo
                for vinculo in imovel_completo.vinculos:
                    pessoa_id = await self.upsert_pessoa(
                        vinculo.cpf, vinculo.nome_completo, conn
                    )
                    
                    await self.upsert_vinculo(imovel_id, pessoa_id, vinculo, conn)
                
                logger.debug(
                    f"Saved complete imovel {imovel_completo.imovel.codigo_incra} "
                    f"with {len(imovel_completo.vinculos)} vinculos"
                )
            
            except Exception as e:
                logger.error(
                    f"Failed to save imovel {imovel_completo.imovel.codigo_incra}: {e}"
                )
                raise
    
    async def bulk_save_imoveis(self, imoveis: List[ImovelCompleto]) -> int:
        """
        Save multiple property records efficiently.
        
        Returns the number of successfully saved records.
        
        Uses transactions for consistency while continuing on individual failures.
        """
        saved_count = 0
        failed_count = 0
        
        for imovel in imoveis:
            try:
                await self.save_imovel_completo(imovel)
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save imovel: {e}")
                failed_count += 1
                continue
        
        logger.info(f"Bulk save complete: {saved_count} saved, {failed_count} failed")
        return saved_count
    
    async def get_imovel_by_codigo(self, codigo_incra: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a complete property record by INCRA code.
        
        Returns a dictionary with property data and vinculos, or None if not found.
        """
        query = """
            SELECT 
                i.codigo_incra,
                i.area_ha,
                i.situacao,
                i.municipio,
                i.uf,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'cpf', p.cpf,
                            'nome_completo', p.nome_completo,
                            'vinculo', v.tipo_vinculo,
                            'participacao_pct', v.participacao_pct
                        ) ORDER BY v.tipo_vinculo, p.nome_completo
                    ) FILTER (WHERE v.id IS NOT NULL),
                    '[]'::json
                ) as vinculos
            FROM imoveis i
            LEFT JOIN vinculos v ON i.id = v.imovel_id
            LEFT JOIN pessoas p ON v.pessoa_id = p.id
            WHERE i.codigo_incra = $1
            GROUP BY i.id, i.codigo_incra, i.area_ha, i.situacao, i.municipio, i.uf
        """
        
        async with self.db.acquire() as conn:
            try:
                row = await conn.fetchrow(query, codigo_incra)
                
                if not row:
                    logger.debug(f"Imovel not found: {codigo_incra}")
                    return None
                
                return dict(row)
            
            except Exception as e:
                logger.error(f"Failed to fetch imovel {codigo_incra}: {e}")
                raise
    
    async def save_extraction_metadata(self, metadata: ExtractionMetadata) -> int:
        """
        Save extraction metadata for auditing and checkpoint recovery.
        
        Returns the ID of the metadata record.
        """
        query = """
            INSERT INTO extraction_metadata (
                uf, municipio, total_registros, arquivo_hash, status, erro_mensagem
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        
        async with self.db.acquire() as conn:
            try:
                metadata_id = await conn.fetchval(
                    query,
                    metadata.uf,
                    metadata.municipio,
                    metadata.total_registros,
                    metadata.arquivo_hash,
                    metadata.status,
                    metadata.erro_mensagem,
                )
                
                logger.info(
                    f"Saved extraction metadata for {metadata.municipio}/{metadata.uf}: "
                    f"{metadata.total_registros} records"
                )
                return metadata_id
            
            except Exception as e:
                logger.error(f"Failed to save extraction metadata: {e}")
                raise
    
    async def get_total_imoveis(self) -> int:
        """Get total count of properties in database."""
        query = "SELECT COUNT(*) FROM imoveis"
        
        async with self.db.acquire() as conn:
            return await conn.fetchval(query)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        query = """
            SELECT 
                COUNT(DISTINCT i.id) as total_imoveis,
                COUNT(DISTINCT p.id) as total_pessoas,
                COUNT(DISTINCT v.id) as total_vinculos,
                COUNT(DISTINCT i.uf) as total_estados,
                COUNT(DISTINCT i.municipio) as total_municipios
            FROM imoveis i
            LEFT JOIN vinculos v ON i.id = v.imovel_id
            LEFT JOIN pessoas p ON v.pessoa_id = p.id
        """
        
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(query)
            return dict(row)
