from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database import get_db
from app.models import GeneralData
from app.schemas import GeneralDataCreate, GeneralDataUpdate, GeneralDataResponse
from app.dependencies import verify_api_key, limiter

router = APIRouter(
    prefix="/api/v1/data",
    tags=["General Data (CRUD)"]
)

@router.get("/", response_model=List[GeneralDataResponse])
async def get_all_data(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Retrieve general data publicly with pagination.
    """
    try:
        query = select(GeneralData).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch records")

@router.get("/{record_id}", response_model=GeneralDataResponse)
async def get_data_by_id(record_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve single record by UUID.
    """
    query = select(GeneralData).filter(GeneralData.id == record_id)
    result = await db.execute(query)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.post("/", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_data(
    request: Request,
    data_in: GeneralDataCreate, 
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new generic record. Requires API Key.
    """
    try:
        new_record = GeneralData(**data_in.model_dump())
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)
        return new_record
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create data")

@router.put("/{record_id}", response_model=GeneralDataResponse)
@limiter.limit("30/minute")
async def update_data(
    request: Request,
    record_id: UUID, 
    data_in: GeneralDataUpdate, 
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a generic record. Requires API Key.
    """
    query = select(GeneralData).filter(GeneralData.id == record_id)
    result = await db.execute(query)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    try:
        update_data = data_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(record, key, value)
            
        await db.commit()
        await db.refresh(record)
        return record
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update data")

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_data(
    request: Request,
    record_id: UUID, 
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a generic record using UUID. Requires API Key.
    """
    query = select(GeneralData).filter(GeneralData.id == record_id)
    result = await db.execute(query)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    try:
        await db.delete(record)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete data")
