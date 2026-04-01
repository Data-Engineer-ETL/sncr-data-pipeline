-- ============================================================================
-- SNCR Database Schema
-- Sistema Nacional de Cadastro Rural
-- 
-- Modelagem: Normalizada (3NF) com tabelas separadas para imóveis e pessoas
-- Performance: Índices otimizados para consultas por código INCRA (SLA < 2s)
-- ============================================================================

-- Extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Tabela: imoveis
-- Armazena informações dos imóveis rurais
-- ============================================================================
CREATE TABLE IF NOT EXISTS imoveis (
    id BIGSERIAL PRIMARY KEY,
    codigo_incra CHAR(17) NOT NULL UNIQUE,  -- Código INCRA tem exatamente 17 dígitos
    area_ha NUMERIC(12, 4) NOT NULL CHECK (area_ha > 0),  -- Área em hectares
    situacao VARCHAR(20) NOT NULL CHECK (situacao IN ('Ativo', 'Inativo', 'Cancelado', 'Suspenso')),
    municipio VARCHAR(100) NOT NULL,
    uf CHAR(2) NOT NULL CHECK (length(uf) = 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comentários
COMMENT ON TABLE imoveis IS 'Imóveis rurais cadastrados no SNCR';
COMMENT ON COLUMN imoveis.codigo_incra IS 'Código único INCRA de 17 dígitos';
COMMENT ON COLUMN imoveis.area_ha IS 'Área do imóvel em hectares (até 4 casas decimais)';
COMMENT ON COLUMN imoveis.situacao IS 'Situação cadastral: Ativo, Inativo, Cancelado ou Suspenso';

-- ============================================================================
-- Tabela: pessoas
-- Armazena informações de proprietários e arrendatários (sem duplicação)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pessoas (
    id BIGSERIAL PRIMARY KEY,
    cpf CHAR(11) NOT NULL UNIQUE,  -- CPF sem formatação (apenas dígitos)
    nome_completo VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comentários
COMMENT ON TABLE pessoas IS 'Pessoas físicas (proprietários e arrendatários)';
COMMENT ON COLUMN pessoas.cpf IS 'CPF sem formatação, apenas 11 dígitos';

-- ============================================================================
-- Tabela: vinculos
-- Relacionamento N:N entre imóveis e pessoas
-- ============================================================================
CREATE TABLE IF NOT EXISTS vinculos (
    id BIGSERIAL PRIMARY KEY,
    imovel_id BIGINT NOT NULL REFERENCES imoveis(id) ON DELETE CASCADE,
    pessoa_id BIGINT NOT NULL REFERENCES pessoas(id) ON DELETE CASCADE,
    tipo_vinculo VARCHAR(20) NOT NULL CHECK (tipo_vinculo IN ('Proprietário', 'Arrendatário')),
    participacao_pct NUMERIC(5, 2) NOT NULL CHECK (participacao_pct >= 0 AND participacao_pct <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Um mesmo CPF não pode ter mais de um vínculo do mesmo tipo no mesmo imóvel
    UNIQUE(imovel_id, pessoa_id, tipo_vinculo)
);

-- Comentários
COMMENT ON TABLE vinculos IS 'Vínculos entre imóveis e pessoas (propriedade ou arrendamento)';
COMMENT ON COLUMN vinculos.tipo_vinculo IS 'Tipo: Proprietário ou Arrendatário';
COMMENT ON COLUMN vinculos.participacao_pct IS 'Percentual de participação (0-100)';

-- ============================================================================
-- Tabela: extraction_metadata
-- Registra metadados de cada extração realizada
-- ============================================================================
CREATE TABLE IF NOT EXISTS extraction_metadata (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uf CHAR(2) NOT NULL,
    municipio VARCHAR(100),
    total_registros INTEGER DEFAULT 0,
    arquivo_hash VARCHAR(64),  -- SHA-256 hash do arquivo CSV
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'partial', 'failed')),
    erro_mensagem TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comentários
COMMENT ON TABLE extraction_metadata IS 'Log de extrações realizadas para auditoria e checkpoint';
COMMENT ON COLUMN extraction_metadata.arquivo_hash IS 'Hash SHA-256 do arquivo extraído';

-- ============================================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================================

-- **ÍNDICE PRINCIPAL: Consulta por código INCRA (requisito de SLA < 2s)**
-- Este é o índice crítico para o requisito de performance da API
-- Justificativa: O endpoint GET /imovel/{codigo_incra} é a consulta principal
CREATE UNIQUE INDEX IF NOT EXISTS idx_imoveis_codigo_incra 
    ON imoveis(codigo_incra);

-- **ÍNDICE: Consultas por localização (UF + Município)**
-- Justificativa: Frequente necessidade de filtrar imóveis por região geográfica
CREATE INDEX IF NOT EXISTS idx_imoveis_uf_municipio 
    ON imoveis(uf, municipio);

-- **ÍNDICE: Consultas por situação**
-- Justificativa: Comum filtrar apenas imóveis ativos
CREATE INDEX IF NOT EXISTS idx_imoveis_situacao 
    ON imoveis(situacao);

-- **ÍNDICE: Busca de pessoa por CPF**
-- Justificativa: Necessário para evitar duplicação de pessoas durante a carga
CREATE UNIQUE INDEX IF NOT EXISTS idx_pessoas_cpf 
    ON pessoas(cpf);

-- **ÍNDICE: Busca de vínculos por imóvel**
-- Justificativa: JOIN frequente para retornar proprietários/arrendatários de um imóvel
CREATE INDEX IF NOT EXISTS idx_vinculos_imovel_id 
    ON vinculos(imovel_id);

-- **ÍNDICE: Busca de vínculos por pessoa**
-- Justificativa: Permite consultar todos os imóveis de uma pessoa
CREATE INDEX IF NOT EXISTS idx_vinculos_pessoa_id 
    ON vinculos(pessoa_id);

-- **ÍNDICE COMPOSTO: Busca de vínculos por imóvel e tipo**
-- Justificativa: Otimiza consultas que filtram por tipo de vínculo
CREATE INDEX IF NOT EXISTS idx_vinculos_imovel_tipo 
    ON vinculos(imovel_id, tipo_vinculo);

-- **ÍNDICE: Log de extrações por UF e timestamp**
-- Justificativa: Auditoria e verificação de checkpoints
CREATE INDEX IF NOT EXISTS idx_extraction_uf_timestamp 
    ON extraction_metadata(uf, timestamp DESC);

-- ============================================================================
-- TRIGGER: Atualizar updated_at automaticamente
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_imoveis_updated_at
    BEFORE UPDATE ON imoveis
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pessoas_updated_at
    BEFORE UPDATE ON pessoas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS: Facilitar consultas comuns
-- ============================================================================

-- View: Imóveis completos com seus vínculos
CREATE OR REPLACE VIEW vw_imoveis_completos AS
SELECT 
    i.id,
    i.codigo_incra,
    i.area_ha,
    i.situacao,
    i.municipio,
    i.uf,
    json_agg(
        json_build_object(
            'cpf', p.cpf,
            'nome_completo', p.nome_completo,
            'vinculo', v.tipo_vinculo,
            'participacao_pct', v.participacao_pct
        ) ORDER BY v.tipo_vinculo, p.nome_completo
    ) FILTER (WHERE v.id IS NOT NULL) AS vinculos
FROM 
    imoveis i
    LEFT JOIN vinculos v ON i.id = v.imovel_id
    LEFT JOIN pessoas p ON v.pessoa_id = p.id
GROUP BY 
    i.id, i.codigo_incra, i.area_ha, i.situacao, i.municipio, i.uf;

COMMENT ON VIEW vw_imoveis_completos IS 'View desnormalizada com imóveis e seus vínculos em JSON';

-- ============================================================================
-- GRANTS (ajustar conforme necessário em produção)
-- ============================================================================
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sncr_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sncr_user;

-- ============================================================================
-- ANÁLISE DE PERFORMANCE
-- ============================================================================
-- Para verificar o plano de execução e garantir SLA < 2s:
-- EXPLAIN ANALYZE SELECT * FROM vw_imoveis_completos WHERE codigo_incra = '12345678901234567';
