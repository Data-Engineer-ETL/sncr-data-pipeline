#!/usr/bin/env python
"""
Script to initialize the database schema.

Usage:
    python scripts/init_db.py
"""
import asyncio
import asyncpg
from pathlib import Path
from loguru import logger

from src.infrastructure.config import get_settings


async def create_database() -> None:
    """Create database if it doesn't exist."""
    settings = get_settings()
    
    # Connect to default 'postgres' database to create our database
    try:
        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database="postgres",
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.POSTGRES_DB,
        )
        
        if not exists:
            # Create database
            await conn.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
            logger.info(f"Database '{settings.POSTGRES_DB}' created")
        else:
            logger.info(f"Database '{settings.POSTGRES_DB}' already exists")
        
        await conn.close()
    
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise


async def run_migrations() -> None:
    """Run SQL migrations to create schema."""
    settings = get_settings()
    
    # Read schema file
    schema_file = Path(__file__).parent.parent / "migrations" / "schema.sql"
    
    if not schema_file.exists():
        logger.error(f"Schema file not found: {schema_file}")
        return
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    # Connect to our database
    try:
        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )
        
        # Execute schema
        await conn.execute(schema_sql)
        logger.info("Schema created successfully")
        
        # Verify tables
        tables = await conn.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        
        logger.info(f"Created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table['table_name']}")
        
        await conn.close()
    
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        raise


async def main() -> None:
    """Main entry point."""
    logger.info("=== Database Initialization ===")
    
    try:
        await create_database()
        await run_migrations()
        logger.info(" Database initialization complete!")
    
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
