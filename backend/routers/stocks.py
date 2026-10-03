import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.stocks import StocksService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/stocks", tags=["stocks"])


# ---------- Pydantic Schemas ----------
class StocksData(BaseModel):
    """Entity data schema (for create/update)"""
    name: str
    code: str
    market: str
    sector: str
    industry: str


class StocksUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    name: Optional[str] = None
    code: Optional[str] = None
    market: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class StocksResponse(BaseModel):
    """Entity response schema"""
    id: int
    name: str
    code: str
    market: str
    sector: str
    industry: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StocksListResponse(BaseModel):
    """List response schema"""
    items: List[StocksResponse]
    total: int
    skip: int
    limit: int


class StocksBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[StocksData]


class StocksBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: StocksUpdateData


class StocksBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[StocksBatchUpdateItem]


class StocksBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=StocksListResponse)
async def query_stockss(
    query: str = Query(None, description='Query conditions as JSON, e.g. {"id":2} or {"id":{"$gte":2}}'),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query stockss with filtering, sorting, and pagination"""
    logger.debug(f"Querying stockss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = StocksService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        
        result = await service.get_list(
            skip=skip, 
            limit=limit,
            query_dict=query_dict,
            sort=sort,
        )
        logger.debug(f"Found {result['total']} stockss")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Invalid stocks query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error querying stockss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=StocksListResponse)
async def query_stockss_all(
    query: str = Query(None, description='Query conditions as JSON, e.g. {"id":2} or {"id":{"$gte":2}}'),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query stockss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying stockss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = StocksService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")

        result = await service.get_list(
            skip=skip,
            limit=limit,
            query_dict=query_dict,
            sort=sort
        )
        logger.debug(f"Found {result['total']} stockss")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Invalid stocks query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error querying stockss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=StocksResponse)
async def get_stocks(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single stocks by ID"""
    logger.debug(f"Fetching stocks with id: {id}, fields={fields}")
    
    service = StocksService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Stocks with id {id} not found")
            raise HTTPException(status_code=404, detail="Stocks not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stocks {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=StocksResponse, status_code=201)
async def create_stocks(
    data: StocksData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new stocks"""
    logger.debug(f"Creating new stocks with data: {data}")
    
    service = StocksService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create stocks")
        
        logger.info(f"Stocks created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating stocks: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating stocks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[StocksResponse], status_code=201)
async def create_stockss_batch(
    request: StocksBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple stockss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} stockss")
    
    service = StocksService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} stockss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[StocksResponse])
async def update_stockss_batch(
    request: StocksBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple stockss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} stockss")
    
    service = StocksService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} stockss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=StocksResponse)
async def update_stocks(
    id: int,
    data: StocksUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing stocks"""
    logger.debug(f"Updating stocks {id} with data: {data}")

    service = StocksService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Stocks with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Stocks not found")
        
        logger.info(f"Stocks {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating stocks {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating stocks {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_stockss_batch(
    request: StocksBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple stockss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} stockss")
    
    service = StocksService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} stockss successfully")
        return {"message": f"Successfully deleted {deleted_count} stockss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_stocks(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single stocks by ID"""
    logger.debug(f"Deleting stocks with id: {id}")
    
    service = StocksService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Stocks with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Stocks not found")
        
        logger.info(f"Stocks {id} deleted successfully")
        return {"message": "Stocks deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting stocks {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")