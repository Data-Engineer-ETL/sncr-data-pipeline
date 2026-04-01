"""
Script auxiliar para executar o scraper do diretório correto.

Este script garante que os módulos sejam encontrados corretamente.

Usage:
    python run_demo.py
"""
import sys
import os
from pathlib import Path

# Muda para o diretório do projeto
project_dir = Path(__file__).parent.resolve()
os.chdir(project_dir)

# Adiciona ao path
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Agora executa o demo_scraper
print(f"📁 Diretório de trabalho: {os.getcwd()}")
print(f"🐍 Python path configurado: {project_dir}\n")

# Importa e executa
if __name__ == "__main__":
    import demo_scraper
    demo_scraper.demo_scraper()
