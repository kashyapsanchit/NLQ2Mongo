from langchain.prompts import PromptTemplate
from src.ai.utils import OutputParser
from src.ai.llm import llm
import logging
import time

logging.basicConfig(level=logging.INFO)

def check_relevance(user_query, prev_data):
    """
    Determines if a cached query is relevant to the new user query.
    Returns True if relevant, False otherwise.
    """

    now = time.time()
    agent = llm()

    logging.info("Checking query relevance")

    # Extract previous user input
    cached_query_text = prev_data.get("user_input", "")

    template = """
    You are an AI agent that determines if two queries have the same intent or not.
    
    - Given a new user query and a cached query, compare them for meaning and intent.
    - If they ask for different things (e.g., one asks for "active users" and another for "inactive users"), return False.
    - If they have the same intent for data, return True.
    
    Respond with JSON format:
    - "intent": true or false.

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    New Query: {user_query}
    Cached Query: {cached_query_text}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """

    relevance_template = PromptTemplate(
        template=template,
        input_variables=["user_query", "cached_query_text"],
    )

    json_parser = OutputParser()

    relevance_chain = relevance_template | agent | json_parser

    result = relevance_chain.invoke({"user_query": user_query, "cached_query_text": cached_query_text})

    if "intent" not in result:
        raise ValueError("Invalid response format from relevance check.")

    end = time.time()
    execution_time = end - now
    print(f"Execution time for Relevance Agent: {execution_time}")

   
    return result["intent"]
