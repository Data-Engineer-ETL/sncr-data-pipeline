"""Response models for the API."""
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class ProprietarioResponse(BaseModel):
    """Response model for property owner/tenant."""
    nome_completo: str = Field(..., description="Full name")
    cpf: str = Field(..., description="Anonymized CPF (e.g., ***.***.*72-45)")
    vinculo: str = Field(..., description="Relationship type (Proprietário or Arrendatário)")
    participacao_pct: Decimal = Field(..., description="Ownership percentage (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome_completo": "Maria Aparecida de Souza",
                "cpf": "***.***.*72-45",
                "vinculo": "Proprietário",
                "participacao_pct": 100.0
            }
        }


class ImovelResponse(BaseModel):
    """Response model for property details."""
    codigo_incra: str = Field(..., description="INCRA property code (17 digits)")
    area_ha: Decimal = Field(..., description="Area in hectares")
    situacao: str = Field(..., description="Property status")
    proprietarios: List[ProprietarioResponse] = Field(
        default_factory=list,
        description="List of owners and tenants"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo_incra": "12345678901234567",
                "area_ha": 142.5,
                "situacao": "Ativo",
                "proprietarios": [
                    {
                        "nome_completo": "Maria Aparecida de Souza",
                        "cpf": "***.***.*72-45",
                        "vinculo": "Proprietário",
                        "participacao_pct": 100.0
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Imóvel não encontrado para o código INCRA fornecido"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    database: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-03-30T10:30:00Z",
                "database": "connected"
            }
        }


class StatsResponse(BaseModel):
    """Statistics response."""
    total_imoveis: int
    total_pessoas: int
    total_vinculos: int
    total_estados: int
    total_municipios: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_imoveis": 15420,
                "total_pessoas": 18350,
                "total_vinculos": 20100,
                "total_estados": 3,
                "total_municipios": 45
            }
        }
