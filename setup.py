"""Setup configuration for SNCR project."""
from setuptools import setup, find_packages

setup(
    name="sncr-pipeline",
    version="1.0.0",
    description="Sistema Nacional de Cadastro Rural - Data Pipeline",
    author="SNCR Team",
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "asyncpg>=0.29.0",
        "psycopg2-binary>=2.9.9",
        "httpx>=0.26.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.3",
        "lxml>=5.1.0",
        "pandas>=2.2.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.2.3",
        "loguru>=0.7.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "black>=24.1.1",
            "ruff>=0.1.14",
            "mypy>=1.8.0",
        ],
        "scraper": [
            "playwright>=1.41.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "sncr-demo=demo_scraper:demo_scraper",
            "sncr-etl=scripts.run_etl:main",
        ],
    },
)
