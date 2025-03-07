from fastapi import APIRouter, HTTPException, Response
from src.backend.schema.query import QuerySchema
from src.backend.db.mongodb import MongoEngine
from src.ai.graphs import execute_workflow
from src.backend.embedding import Embedding
from src.ai.agents.misc import check_relevance
import logging

logging.basicConfig(level=logging.INFO)
query_router = APIRouter()


@query_router.post('/query')
async def query(request: QuerySchema):
    """
    Handles query requests:
    1. Checks if the query exists in the cache and fetches the result.
    2. If not cached, triggers the LLM workflow to generate the query.
    3. Executes the query on the database and returns the results.
    """

    # Initialize services
    engine = MongoEngine()
    embedding = Embedding()

    # Extract request parameters
    user_input = request.query
    skip = request.skip
    limit = request.limit

    if not user_input:
        raise HTTPException(status_code=400, detail="The query is empty or missing. Please provide a valid input.")

    # Check if query exists in cache using RAG and is relevant  
    try:
        prev_data = embedding.get_similar(user_input)
        relevance = check_relevance(user_input, prev_data) if prev_data else False
    except Exception as e:
        logging.info(f"Error fetching cached data: {str(e)}")
        relevance = prev_data = False

    # Case 1: Query found in cache and is relevant
    if prev_data and relevance:
        state = {
            "is_cached": True,
            "mongo_query": prev_data["query"],
            "aggregate": prev_data["aggregate"],
            "collection_name": prev_data['collection_name'],
            "skip": skip,
            "limit": limit
        }

        try:
            state = engine.execute_query(state)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database query execution failed: {str(e)}")

        data = state.get("data")
        status = state.get('execution_status')

        if not data['results']:
            return Response(content="Data not found!", status_code=404)

        if not status:
            return Response(content="Query Execution Failed. Please check the query", status_code=500)

        total_items = data['total_items']

        return {
            "data": data,
            "total": total_items,
            "skip": skip,
            "limit": limit,
        }

    # Case 2: Query not found in cache - Execute Generation Graph
    state = {"user_query": str(user_input), 'retry_count': 0, 'skip':skip, 'limit': limit }

    try:
        state = await execute_workflow(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

    if not state['execution_status']:
        raise HTTPException(status_code=500, detail="Generation and Execution Failed.")

    data = state['data']

    if not data['results']:
        return Response(content="Data not found", status_code=404)

    # Save the newly generated query to the database for caching
    query_data = {
        "user_input": user_input,
        "query": state['mongo_query'].get('query'),
        "aggregate": state['aggregate'],
        "collection_name": state['collection_name'][0],
    }

    try:
        if not embedding.store_embeddings(query_data):
            raise HTTPException(status_code=400, detail="Failed to save query data in the database.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving query data: {str(e)}")

    return {
        "data": data,
        "total": data['total_items'],
        "skip": skip,
        "limit": limit,
    }
