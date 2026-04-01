"""
Script de demonstração do scraper (sem banco de dados).

Mostra o funcionamento da extração de dados do site SNCR
sem necessidade de PostgreSQL ou Docker.

Usage:
    python demo_scraper.py
"""
import sys
from pathlib import Path

# IMPORTANTE: Adiciona o diretório raiz ao sys.path
# Isso permite importar módulos de 'src' independente de onde o script é executado
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adapters.scraper import SNCRScraper
from src.infrastructure.config import get_settings
from loguru import logger
import json


def demo_scraper():
    """Demonstração do scraper."""
    print("=" * 70)
    print("🔍 DEMONSTRAÇÃO DO SCRAPER SNCR")
    print("=" * 70)
    print("\nEste script demonstra a extração de dados do site SNCR")
    print("Os dados serão apenas exibidos no console (sem salvar no banco)\n")
    
    # Configurações
    settings = get_settings()
    
    print(f"📍 Site alvo: {settings.BASE_URL}")
    print(f"🌎 Estados configurados: {settings.TARGET_STATES}")
    print(f"🔄 Max retries: {settings.MAX_RETRIES}")
    print(f"⏱️  Timeout: {settings.REQUEST_TIMEOUT}s")
    print(f"💾 Checkpoint dir: {settings.CHECKPOINT_DIR}\n")
    
    # Pergunta qual estado extrair (para demo rápida)
    print("─" * 70)
    print("Para demonstração, vamos extrair apenas 1 município de 1 estado.")
    print("─" * 70)
    
    # Usa apenas o primeiro estado configurado
    estados = settings.target_states_list
    if not estados:
        print("❌ Nenhum estado configurado em TARGET_STATES (.env)")
        print("   Configure: TARGET_STATES=SP,MG,RJ")
        return
    
    uf = estados[0]  # Primeiro estado
    print(f"\n🎯 Estado selecionado: {uf}\n")
    
    # Inicia scraper
    print("🚀 Iniciando scraper...\n")
    
    try:
        with SNCRScraper() as scraper:
            # Inicializa sessão
            print("1️⃣  Inicializando sessão HTTP...")
            scraper.initialize_session()
            print("   ✅ Sessão inicializada\n")
            
            # Busca municípios
            print(f"2️⃣  Buscando municípios de {uf}...")
            municipios = scraper.get_municipios(uf)
            
            if not municipios:
                print(f"   ❌ Nenhum município encontrado para {uf}")
                print("   ⚠️  Nota: O site pode estar indisponível ou usar captcha")
                return
            
            print(f"   ✅ Encontrados {len(municipios)} municípios:")
            for i, mun in enumerate(municipios[:5], 1):  # Mostra apenas 5
                print(f"      {i}. {mun}")
            if len(municipios) > 5:
                print(f"      ... e mais {len(municipios) - 5} municípios")
            print()
            
            # Extrai dados do primeiro município (demo)
            municipio = municipios[0]
            print(f"3️⃣  Extraindo dados de {municipio}/{uf}...")
            print("   ⏳ Baixando CSV... (pode levar alguns segundos)")
            
            try:
                df = scraper.download_csv(uf, municipio)
                
                if df is None or df.empty:
                    print(f"   ⚠️  Nenhum dado encontrado para {municipio}/{uf}")
                    print("   💡 Isso pode ser normal se o município não tem imóveis cadastrados")
                else:
                    print(f"   ✅ Dados extraídos com sucesso!\n")
                    
                    # Mostra estatísticas
                    print("📊 ESTATÍSTICAS DOS DADOS EXTRAÍDOS")
                    print("─" * 70)
                    print(f"   Total de registros: {len(df)}")
                    print(f"   Colunas: {list(df.columns)}")
                    print()
                    
                    # Mostra preview dos dados
                    print("📄 PREVIEW DOS DADOS (primeiras 3 linhas)")
                    print("─" * 70)
                    print(df.head(3).to_string())
                    print()
                    
                    # Salva CSV para inspeção
                    output_file = f"demo_data_{uf}_{municipio.replace(' ', '_')}.csv"
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"💾 Dados salvos em: {output_file}")
                    print(f"   👀 Você pode abrir este arquivo no Excel para inspecionar\n")
                    
                    # Mostra exemplo de registro
                    if len(df) > 0:
                        print("🔍 EXEMPLO DE REGISTRO")
                        print("─" * 70)
                        registro = df.iloc[0].to_dict()
                        for chave, valor in registro.items():
                            print(f"   {chave}: {valor}")
                        print()
            
            except Exception as e:
                print(f"   ❌ Erro ao extrair dados: {e}")
                print(f"   💡 Possíveis causas:")
                print(f"      - Site SNCR indisponível")
                print(f"      - Bloqueio anti-bot")
                print(f"      - Timeout de rede")
                logger.error(f"Erro na extração: {e}", exc_info=True)
                return
        
        # Sucesso!
        print("=" * 70)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print()
        print("📝 O que você viu:")
        print("   ✓ Inicialização da sessão HTTP")
        print("   ✓ Listagem de municípios por estado")
        print("   ✓ Download e parse de CSV")
        print("   ✓ Estrutura dos dados extraídos")
        print()
        print("🔧 Recursos implementados (não mostrados aqui):")
        print("   ✓ Retry automático com backoff exponencial")
        print("   ✓ Detecção de anti-bot")
        print("   ✓ Checkpoint para recovery")
        print("   ✓ Logging estruturado")
        print("   ✓ Rate limiting (1s entre requests)")
        print()
        print("🚀 Para processar todos os estados e municípios:")
        print("   1. Configure PostgreSQL (ou use Docker)")
        print("   2. Execute: python scripts/run_etl.py")
        print("   3. Ou com Docker: docker-compose --profile etl up etl")
        print()
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        logger.error(f"Erro na demonstração: {e}", exc_info=True)


if __name__ == "__main__":
    # Configura logging mais limpo para demo
    logger.remove()  # Remove handler padrão
    logger.add(
        sys.stderr,
        format="<dim>{time:HH:mm:ss}</dim> | <level>{level: <8}</level> | <level>{message}</level>",
        level="WARNING",  # Apenas warnings e errors no console
    )
    
    try:
        demo_scraper()
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        logger.exception("Erro fatal")
