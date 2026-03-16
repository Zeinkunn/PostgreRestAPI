from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from app.database import get_db
from app.models import AgentMemory
from app.schemas import AgentMemoryCreate, AgentMemoryResponse, AgentMemorySearch, AgentMemorySearchResponse
from app.dependencies import verify_api_key, limiter

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/memories",
    tags=["Agent Memories (Vector DB)"]
)

@router.post("/", response_model=AgentMemoryResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def ingest_memory(
    request: Request,
    memory_in: AgentMemoryCreate, 
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    try:
        new_memory = AgentMemory(
            persona_id=memory_in.persona_id,
            content=memory_in.content,
            embedding=memory_in.embedding
        )
        db.add(new_memory)
        await db.commit()
        await db.refresh(new_memory)
        return new_memory
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to insert memory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/search", response_model=List[AgentMemorySearchResponse])
@limiter.limit("60/minute")
async def search_memory(request: Request, search_params: AgentMemorySearch, db: AsyncSession = Depends(get_db)):
    try:
        # Use pgvector's cosine distance operator (<=>)
        # Calculate distance = 1 - cosine_similarity. Sort ascending.
        distance_expr = AgentMemory.embedding.cosine_distance(search_params.query_embedding)
        
        query = select(AgentMemory, distance_expr.label("distance"))
        
        # Pre-filter by persona_id if provided
        if search_params.persona_id:
            query = query.filter(AgentMemory.persona_id == search_params.persona_id)
            
        query = query.order_by(distance_expr).limit(search_params.limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        formatted_results = []
        for memory, distance in rows:
            formatted_results.append({
                "id": memory.id,
                "persona_id": memory.persona_id,
                "content": memory.content,
                "created_at": memory.created_at,
                "distance": distance
            })
            
        return formatted_results
    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
