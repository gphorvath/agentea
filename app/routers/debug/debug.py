"""Debug router for the API."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.utils.db import postgres


router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/db_check")
async def db_check() -> Dict[str, Any]:
    """
    Check database connection and return test data.

    This endpoint tests the connection to the PostgreSQL database
    and returns data from the test_items table.
    """
    try:
        # Test basic connection with a simple query
        result = await postgres.fetch_one("SELECT 1 as connection_test")
        if not result or result.get("connection_test") != 1:
            raise HTTPException(
                status_code=500, detail="Database connection test failed"
            )

        # Get data from test_items table
        items = await postgres.fetch_all(
            "SELECT id, name, description, created_at, updated_at FROM test_items"
        )

        return {
            "status": "ok",
            "connection_test": True,
            "items_count": len(items),
            "items": items,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/db_add_item")
async def db_add_item(name: str, description: str = None) -> Dict[str, Any]:
    """
    Add a new item to the test_items table.

    This endpoint adds a new item to the test_items table and returns the created item.

    Args:
        name: The name of the item
        description: Optional description of the item
    """
    try:
        # Insert new item
        await postgres.execute(
            "INSERT INTO test_items (name, description) VALUES (:name, :description)",
            {"name": name, "description": description},
        )

        # Get the newly created item
        item = await postgres.fetch_one(
            "SELECT id, name, description, created_at, updated_at FROM test_items "
            "WHERE name = :name ORDER BY id DESC LIMIT 1",
            {"name": name},
        )

        return {"status": "ok", "message": "Item added successfully", "item": item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
