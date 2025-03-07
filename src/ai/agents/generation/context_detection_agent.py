from langchain.prompts import PromptTemplate
from src.ai.utils import OutputParser, count_tokens
from src.ai.config import COLLECTIONS
from src.ai.llm import llm
import logging
import ast
import time

logging.basicConfig(level=logging.INFO)

class ContextDetectionAgent:

    def __init__(self):
        self.llm = llm()

    def context_detection(self, state):
        logging.info("Detecting Context and Intent from User Query")

        now = time.time()
        user_query=state["user_query"]
        collections = ast.literal_eval(COLLECTIONS)

        template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
        Given the following MongoDB collections: {collections}, your task is to:
        1. Analyze the natural language query provided below and determine whether it explicitly or implicitly refers to one or two collections from the list of collections. 
        - A query may involve two collections if it mentions entities that could logically be linked (e.g., referencing one collection and filtering based on another collection's data).
        - Examples of indirect references include queries that require relationships, such as "proposals" for a specific "organization" or "users" associated with an "organization.".
        2. If the query refers to two collections, set the "aggregate" field to `True` and set the "collection_name" field to a list of collections referred to in the natural language query.
        3. If only one collection is being referred to, set the "aggregate" field to `False` and the "collection_name" field to the name of that collection in a list.
        4. Analyze the intent of the query by identifying:
        - The primary action (e.g., 'retrieve', 'count', 'filter', 'compare', 'aggregate')
        - Any conditions or filters (e.g., 'active status', 'date range', 'specific value')
        - Any specific fields of interest
        - Any sorting or ordering requirements
        - Any grouping requirements
        Store these intents as a list of descriptive strings.

        When making your determination, consider:
        - Explicit mentions of collection names or their synonyms (e.g., "organization" for "organizations").
        - Implied relationships or hierarchies between entities described in the query.
        - Usually, in the nlp_query, the first collection mentioned will be the main collection for which data will be required so store that first in the list.
        - Contextual clues that suggest joining or aggregating data from more than one collection.
        - Negations or inverse conditions in the query.
        - Temporal aspects (e.g., 'current', 'past', 'future').
        - Comparative operations (e.g., 'more than', 'less than', 'between').

        Return the result in JSON format with the following keys:
        - 'collection_name': The list of most relevant collection(s) to the query (either the first mentioned collection if two collections are involved or the single collection being referred to).
        - 'aggregate': `True` if the query involves two collections, `False` otherwise.

        <|eot_id|><|start_header_id|>user<|end_header_id|>
        natural language query: {user_query} \n\n
        <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

        context_template = PromptTemplate(
            template=template,
            input_variables=["collections","user_query"],
        )

        json_parser = OutputParser()
        
        context_chain = context_template | self.llm | json_parser

        chain_inputs = {
            "collections":collections,
            "user_query": user_query
        }

        input_text = context_template.format(**chain_inputs)
        context_final = context_chain.invoke(chain_inputs)

        if not 'collection_name' and 'aggregate' in context_final.keys():
            raise ValueError("Invalid response format from context chain.")

        state['collection_name'] = context_final["collection_name"]
        state['aggregate'] = context_final["aggregate"]
        
        end = time.time()
        execution_time = end - now

        print(f"Execution time for Context Agent: {execution_time}")
        print(f"Token Usage Data: {count_tokens(input_text, context_final)}")

        return {**state}
    

