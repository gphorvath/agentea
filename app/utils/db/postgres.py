"""PostgreSQL client implementation using psycopg."""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, TypeVar, Union

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config.postgres_config import PostgresSettings

# Type variable for generic return types
T = TypeVar("T")

# Configure logger
logger = logging.getLogger(__name__)

# Global connection pool
pool: Optional[AsyncConnectionPool] = None


async def init_db() -> None:
    """Initialize the database connection pool.

    This should be called during application startup.
    """
    global pool

    if pool is not None:
        logger.warning("Database connection pool already initialized")
        return

    # Get PostgreSQL settings
    settings = PostgresSettings()

    # Create connection string
    conninfo = (
        f"postgresql://{settings.user}:{settings.password}@"
        f"{settings.host}:{settings.port}/{settings.database}"
    )

    # Initialize connection pool
    logger.info("Initializing PostgreSQL connection pool")
    pool = AsyncConnectionPool(
        conninfo=conninfo,
        min_size=1,
        max_size=10,
        kwargs={"row_factory": dict_row},
    )

    # Test connection
    try:
        async with pool.connection() as conn:
            await conn.execute("SELECT 1")
        logger.info("Successfully connected to PostgreSQL")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


async def close_db() -> None:
    """Close the database connection pool.

    This should be called during application shutdown.
    """
    global pool

    if pool is None:
        logger.warning("No database connection pool to close")
        return

    logger.info("Closing PostgreSQL connection pool")
    await pool.close()
    pool = None


@asynccontextmanager
async def get_connection():
    """Get a connection from the pool.

    This is a context manager that acquires a connection from the pool,
    yields it, and then releases it back to the pool.

    Yields:
        Connection: A database connection from the pool.
    """
    if pool is None:
        raise RuntimeError("Database connection pool not initialized")

    async with pool.connection() as conn:
        yield conn


async def fetch_one(
    query: str, params: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Execute a query and return the first row.

    Args:
        query: SQL query to execute
        params: Query parameters

    Returns:
        The first row as a dictionary, or None if no rows were returned
    """
    async with get_connection() as conn:
        result = await conn.execute(query, params)
        row = await result.fetchone()
        return row


async def fetch_all(
    query: str, params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Execute a query and return all rows.

    Args:
        query: SQL query to execute
        params: Query parameters

    Returns:
        All rows as a list of dictionaries
    """
    async with get_connection() as conn:
        result = await conn.execute(query, params)
        rows = await result.fetchall()
        return rows


async def execute(
    query: str, params: Optional[Dict[str, Any]] = None
) -> Union[str, int]:
    """Execute a query and return the status or row count.

    Args:
        query: SQL query to execute
        params: Query parameters

    Returns:
        The command status string or row count
    """
    async with get_connection() as conn:
        result = await conn.execute(query, params)
        return result.command_status or result.rowcount


async def execute_many(query: str, params_list: List[Dict[str, Any]]) -> None:
    """Execute a query multiple times with different parameters.

    Args:
        query: SQL query to execute
        params_list: List of parameter dictionaries
    """
    async with get_connection() as conn:
        # Use a transaction to ensure all operations succeed or fail together
        async with conn.transaction():
            for params in params_list:
                await conn.execute(query, params)


async def execute_transaction(queries: List[Dict[str, Any]]) -> None:
    """Execute multiple queries in a transaction.

    Each dictionary in the queries list should have:
    - 'query': The SQL query to execute
    - 'params': (Optional) The parameters for the query

    Args:
        queries: List of query dictionaries
    """
    async with get_connection() as conn:
        # Use a transaction to ensure all operations succeed or fail together
        async with conn.transaction():
            for query_dict in queries:
                sql = query_dict["query"]
                params = query_dict.get("params")
                await conn.execute(sql, params)
