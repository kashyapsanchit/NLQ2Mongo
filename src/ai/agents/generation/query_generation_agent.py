from langchain.prompts import PromptTemplate
from src.backend.db import MongoEngine
from src.ai.utils import OutputParser, relationships, sample_aggregation, count_tokens
from src.ai.agents.prompts import query_generation_template
from src.ai.llm import llm
import logging
import time

logging.basicConfig(level=logging.INFO)

class QueryGenerationAgent:
    def __init__(self):
        self.llm = llm()
        self.mongo = MongoEngine()

    def query_generator(self, state):
        logging.info("Generating Query")
        
        now = time.time()
        schema_data = {}
        relations = []

        collection_name = state["collection_name"]
        user_query = state["user_query"]
        aggregate = state["aggregate"]

        for collection in collection_name:
            schema_data[collection] = self.mongo._get_collection_metadata(collection)
            relations.append(relationships(collection)) 

        # old_query_data = str(self.mongo_obj.fetch_query_data())

        json_parser = OutputParser()

        query_generation_prompt = PromptTemplate(
            template=query_generation_template,
            input_variables=["schema_data", "user_query", "relations", "aggregate", "sample_aggregation"],
        )

        query_generation_chain = query_generation_prompt | self.llm | json_parser

        chain_inputs = {
            "schema_data": schema_data,
            "user_query": user_query,
            "relations": relations,
            "aggregate": aggregate,
            "sample_aggregation": sample_aggregation
        }

        input_text = query_generation_prompt.format(**chain_inputs)

        # Run the chain with the given inputs
        mongo_query = query_generation_chain.invoke(chain_inputs)
        
        if 'query' not in mongo_query.keys():
            raise ValueError("Query generation failed")

        print("************Generated Query***************")
        print(mongo_query)

        end = time.time()
        execution_time = end-now
        print(f"Execution time for query generation: {execution_time}")
        print(f"Token Usage Data: {count_tokens(input_text, mongo_query)}")
        
        return {
            **state,
            "mongo_query": mongo_query
        }
