from langchain.prompts import PromptTemplate
from src.backend.db import MongoEngine
from src.ai.utils import OutputParser, count_tokens
from src.ai.llm import llm
from src.ai.utils import relationships
import logging
import time

logging.basicConfig(level=logging.INFO)

class ImprovementAgent:
    def __init__(self):
        self.llm = llm()
        self.mongo = MongoEngine()

    def improve_query(self, state):
        logging.info(f"Trying to Improve MongoDB Query; count:{state['retry_count']}")
        now = time.time()
        
        schema_data = {}
        relations = []
        
        collection_name = state["collection_name"]
        user_query = state["user_query"]
        aggregate = state["aggregate"]
        mongo_query = state["mongo_query"]

        for collection in collection_name:
            schema_data[collection] = self.mongo._get_collection_metadata(collection)
            relations.append(relationships(collection)) 

        json_parser = OutputParser()
        
        improvement_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
        You are an expert MongoDB query optimizer. Your task is to improve the given mongo_query based on the below strategies.
        
        The goal is to enhance accuracy, relevance, coherence, and maintainability while keeping the intent of user_query intact.

        **Improvement Strategy:**
        
        - **Fix Accuracy Issues:** Ensure the query correctly reflects user intent and aligns with schema_data.
        - **Enhance Relevance:** Ensure necessary filters are included and no redundant conditions exist.
        - **Improve Coherence:** Ensure syntax is correct, joins are efficient, and aggregation is structured properly.
        - **Boost Maintainability:** Simplify query structure without losing functionality if needed.
        - **Case Sensitivity:** Check if case sensitivity is applied properly or not.

        **Inputs:**
        {mongo_query} - The original MongoDB query to improve.
        {user_query} - The natural language query describing user intent.
        {schema_data} - Collection metadata for schema validation.
        {aggregate} - Boolean indicating if the query involves multiple collections.
        {relations} - Relationships between collections for joins.

        **Output JSON Format:**
        {{
            "improved_query": "The refined and optimized MongoDB query"
        }}

        **Task:**
        Improve the provided mongo_query based on the above strategies and return the optimized query.
        <|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """

        improvement_prompt = PromptTemplate(
            template=improvement_template,
            input_variables=["mongo_query", "user_query", "aggregate", "schema_data", "relations"],
        )

        improvement_chain = improvement_prompt | self.llm | json_parser

        input_chain = {
            "mongo_query": mongo_query,
            "user_query": user_query,
            "aggregate": aggregate,
            "schema_data": schema_data,
            "relations": relations
        }

        try:
            improved_query = improvement_chain.invoke(input_chain)
        except Exception as e:
            raise ValueError(f"Error during query improvement: {str(e)}")
        
        input_text = improvement_template.format(**input_chain)

        end = time.time()
        logging.info(f"Token Usage Data: {count_tokens(input_text, improved_query)}")
        logging.info(f"Execution time for improvement agent: {end - now}")
        logging.info("Improved Query")
        logging.info(improved_query)
        
        state['mongo_query'] = improved_query
        
        return {
            **state,
        }
