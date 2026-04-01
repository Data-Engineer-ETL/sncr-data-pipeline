"""Basic tests for domain models."""
import pytest
from decimal import Decimal

from src.domain.models import Imovel, Pessoa, VinculoPessoa, TipoVinculo, SituacaoImovel


class TestPessoa:
    """Tests for Pessoa model."""
    
    def test_validate_cpf(self):
        """Test CPF validation."""
        pessoa = Pessoa(cpf="12345678901", nome_completo="João Silva")
        assert pessoa.cpf == "12345678901"
    
    def test_cpf_with_formatting(self):
        """Test CPF with formatting is cleaned."""
        pessoa = Pessoa(cpf="123.456.789-01", nome_completo="João Silva")
        assert pessoa.cpf == "12345678901"
    
    def test_invalid_cpf_length(self):
        """Test invalid CPF length raises error."""
        with pytest.raises(ValueError, match="CPF deve ter 11 dígitos"):
            Pessoa(cpf="123456", nome_completo="João Silva")
    
    def test_anonymize_cpf(self):
        """Test CPF anonymization."""
        cpf = "12345678972"
        anonymized = Pessoa.anonymize_cpf(cpf)
        assert anonymized == "***.***.*72-72"
        
        # Should show last 2 digits before verifier
        cpf2 = "98765432109"
        anonymized2 = Pessoa.anonymize_cpf(cpf2)
        assert anonymized2 == "***.***.*10-09"


class TestImovel:
    """Tests for Imovel model."""
    
    def test_valid_imovel(self):
        """Test valid imovel creation."""
        imovel = Imovel(
            codigo_incra="12345678901234567",
            area_ha=Decimal("100.5"),
            situacao=SituacaoImovel.ATIVO,
            municipio="Campinas",
            uf="SP",
        )
        assert imovel.codigo_incra == "12345678901234567"
        assert imovel.area_ha == Decimal("100.5")
        assert imovel.uf == "SP"
    
    def test_invalid_codigo_incra(self):
        """Test invalid codigo_incra raises error."""
        with pytest.raises(ValueError, match="Código INCRA deve ter 17 dígitos"):
            Imovel(
                codigo_incra="123",
                area_ha=Decimal("100"),
                situacao=SituacaoImovel.ATIVO,
                municipio="Campinas",
                uf="SP",
            )
    
    def test_negative_area(self):
        """Test negative area raises error."""
        with pytest.raises(ValueError, match="Área deve ser positiva"):
            Imovel(
                codigo_incra="12345678901234567",
                area_ha=Decimal("-10"),
                situacao=SituacaoImovel.ATIVO,
                municipio="Campinas",
                uf="SP",
            )
    
    def test_uf_normalization(self):
        """Test UF is normalized to uppercase."""
        imovel = Imovel(
            codigo_incra="12345678901234567",
            area_ha=Decimal("100"),
            situacao=SituacaoImovel.ATIVO,
            municipio="Campinas",
            uf="sp",
        )
        assert imovel.uf == "SP"


class TestVinculoPessoa:
    """Tests for VinculoPessoa model."""
    
    def test_valid_vinculo(self):
        """Test valid vinculo creation."""
        vinculo = VinculoPessoa(
            cpf="12345678901",
            nome_completo="João Silva",
            vinculo=TipoVinculo.PROPRIETARIO,
            participacao_pct=Decimal("50.0"),
        )
        assert vinculo.participacao_pct == Decimal("50.0")
    
    def test_invalid_participacao_over_100(self):
        """Test participacao > 100 raises error."""
        with pytest.raises(ValueError, match="Participação deve estar entre 0 e 100"):
            VinculoPessoa(
                cpf="12345678901",
                nome_completo="João Silva",
                vinculo=TipoVinculo.PROPRIETARIO,
                participacao_pct=Decimal("150.0"),
            )
    
    def test_invalid_participacao_negative(self):
        """Test negative participacao raises error."""
        with pytest.raises(ValueError, match="Participação deve estar entre 0 e 100"):
            VinculoPessoa(
                cpf="12345678901",
                nome_completo="João Silva",
                vinculo=TipoVinculo.PROPRIETARIO,
                participacao_pct=Decimal("-10.0"),
            )
