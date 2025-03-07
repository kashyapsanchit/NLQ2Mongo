from pydantic import BaseModel
from fastapi import Query
from typing import Optional

class QuerySchema(BaseModel):
    query: str
    skip: int = Query(0, ge=0)
    limit: int = Query(10, ge=1, le=1000)
    # token: Optional[str]
