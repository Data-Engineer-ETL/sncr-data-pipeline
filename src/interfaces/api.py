"""FastAPI application for SNCR data API."""
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger

from src.infrastructure.database import db
from src.infrastructure.config import get_settings
from src.adapters.repository import ImovelRepository
from src.domain.models import Pessoa
from src.interfaces.schemas import (
    ImovelResponse,
    ProprietarioResponse,
    ErrorResponse,
    HealthResponse,
    StatsResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up API...")
    await db.connect()
    logger.info("Database connected")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    await db.disconnect()
    logger.info("Database disconnected")


# Create FastAPI application
app = FastAPI(
    title="SNCR API",
    description="API para consulta de dados do Sistema Nacional de Cadastro Rural",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor"},
    )


# Routes
@app.get(
    "/",
    response_model=dict,
    summary="API Root",
    description="Returns API information and available endpoints",
)
async def root() -> dict:
    """API root endpoint."""
    return {
        "name": "SNCR API",
        "version": "1.0.0",
        "description": "Sistema Nacional de Cadastro Rural - API de Consulta",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "imovel": "/imovel/{codigo_incra}",
            "docs": "/docs",
        },
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check API and database health status",
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        # Test database connection
        repository = ImovelRepository(db)
        await repository.get_total_imoveis()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            database="connected",
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            database="disconnected",
        )


@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Database Statistics",
    description="Get statistics about stored data",
)
async def get_statistics() -> StatsResponse:
    """Get database statistics."""
    try:
        repository = ImovelRepository(db)
        stats = await repository.get_statistics()
        
        return StatsResponse(**stats)
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar estatísticas",
        )


@app.get(
    "/imovel/{codigo_incra}",
    response_model=ImovelResponse,
    responses={
        200: {
            "description": "Property found",
            "model": ImovelResponse,
        },
        404: {
            "description": "Property not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid INCRA code format",
            "model": ErrorResponse,
        },
    },
    summary="Get Property by INCRA Code",
    description="Retrieve detailed information about a property using its INCRA code (17 digits)",
)
async def get_imovel(codigo_incra: str) -> ImovelResponse:
    """
    Get property details by INCRA code.
    
    Args:
        codigo_incra: 17-digit INCRA property code
    
    Returns:
        Property details with anonymized CPFs
    
    Raises:
        HTTPException: 404 if property not found, 422 if invalid format
    """
    # Validate codigo_incra format
    codigo_clean = "".join(filter(str.isdigit, codigo_incra))
    
    if len(codigo_clean) != 17:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Código INCRA deve ter exatamente 17 dígitos",
        )
    
    # Query database
    try:
        repository = ImovelRepository(db)
        imovel_data = await repository.get_imovel_by_codigo(codigo_clean)
        
        if not imovel_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imóvel não encontrado para o código INCRA fornecido",
            )
        
        # Transform vinculos with CPF anonymization
        proprietarios = []
        
        for vinculo in imovel_data.get("vinculos", []):
            cpf_anonimizado = Pessoa.anonymize_cpf(vinculo["cpf"])
            
            proprietarios.append(
                ProprietarioResponse(
                    nome_completo=vinculo["nome_completo"],
                    cpf=cpf_anonimizado,
                    vinculo=vinculo["vinculo"],
                    participacao_pct=Decimal(str(vinculo["participacao_pct"])),
                )
            )
        
        # Build response
        response = ImovelResponse(
            codigo_incra=imovel_data["codigo_incra"],
            area_ha=Decimal(str(imovel_data["area_ha"])),
            situacao=imovel_data["situacao"],
            proprietarios=proprietarios,
        )
        
        logger.info(f"Property retrieved successfully: {codigo_incra}")
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Failed to retrieve property {codigo_incra}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar imóvel",
        )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "src.interfaces.api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
