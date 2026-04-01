"""Domain models for SNCR data."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TipoVinculo(str, Enum):
    """Tipo de vínculo com o imóvel."""
    PROPRIETARIO = "Proprietário"
    ARRENDATARIO = "Arrendatário"


class SituacaoImovel(str, Enum):
    """Situação cadastral do imóvel."""
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    CANCELADO = "Cancelado"
    SUSPENSO = "Suspenso"


class Pessoa(BaseModel):
    """Entidade representando uma pessoa física."""
    cpf: str = Field(..., description="CPF do proprietário/arrendatário")
    nome_completo: str = Field(..., description="Nome completo")
    
    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        """Valida formato do CPF."""
        # Remove formatação
        cpf_clean = "".join(filter(str.isdigit, v))
        if len(cpf_clean) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return cpf_clean
    
    @staticmethod
    def anonymize_cpf(cpf: str) -> str:
        """
        Anonimiza CPF, mostrando apenas os 2 últimos dígitos antes do verificador.
        Exemplo: 12345678972 -> ***.***.**-72
        """
        if len(cpf) != 11:
            return "***.***.***-**"
        
        # Formato: ***.***.*DD-VV onde DD são os 2 últimos dígitos, VV verificador
        last_two = cpf[7:9]
        verifier = cpf[9:11]
        return f"***.***.*{last_two}-{verifier}"


class VinculoPessoa(BaseModel):
    """Vínculo entre pessoa e imóvel."""
    cpf: str
    nome_completo: str
    vinculo: TipoVinculo
    participacao_pct: Decimal = Field(..., description="Percentual de participação")
    
    @field_validator("participacao_pct")
    @classmethod
    def validate_participacao(cls, v: Decimal) -> Decimal:
        """Valida que participação está entre 0 e 100."""
        if not (0 <= v <= 100):
            raise ValueError("Participação deve estar entre 0 e 100")
        return v


class Imovel(BaseModel):
    """Entidade representando um imóvel rural."""
    codigo_incra: str = Field(..., description="Código INCRA do imóvel (17 dígitos)")
    area_ha: Decimal = Field(..., description="Área em hectares")
    situacao: SituacaoImovel = Field(..., description="Situação cadastral")
    municipio: str = Field(..., description="Nome do município")
    uf: str = Field(..., max_length=2, description="Sigla do estado")
    
    @field_validator("codigo_incra")
    @classmethod
    def validate_codigo_incra(cls, v: str) -> str:
        """Valida formato do código INCRA."""
        codigo_clean = "".join(filter(str.isdigit, v))
        if len(codigo_clean) != 17:
            raise ValueError("Código INCRA deve ter 17 dígitos")
        return codigo_clean
    
    @field_validator("area_ha")
    @classmethod
    def validate_area(cls, v: Decimal) -> Decimal:
        """Valida que área é positiva."""
        if v <= 0:
            raise ValueError("Área deve ser positiva")
        return v
    
    @field_validator("uf")
    @classmethod
    def validate_uf(cls, v: str) -> str:
        """Normaliza UF para uppercase."""
        return v.upper()


class ImovelCompleto(BaseModel):
    """Imóvel com seus vínculos de pessoas."""
    imovel: Imovel
    vinculos: list[VinculoPessoa] = Field(default_factory=list)


class ExtractionMetadata(BaseModel):
    """Metadados de uma extração."""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uf: str
    municipio: Optional[str] = None
    total_registros: int = 0
    arquivo_hash: Optional[str] = None
    status: str = Field(default="success")
    erro_mensagem: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
