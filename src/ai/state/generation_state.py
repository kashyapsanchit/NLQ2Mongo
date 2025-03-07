from typing import TypedDict, Dict, Optional


class GenerationState(TypedDict):
    user_query: str
    relations: Dict
    mongo_query:str
    collection_name: str
    aggregate: bool
    execution_status: bool
    data: Dict
    retry_count: int
    skip: int
    limit: int
