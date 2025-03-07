from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import OutputParserException
import tiktoken
import json
import re

class OutputParser(JsonOutputParser):
    def parse(self, text: str) -> dict:
        """
        Parses MongoDB-style JSON with constructs like ISODate into valid JSON.
        """
        try:
            # Step 1: Remove code block formatting (if present)
            if text.startswith("```json"):
                text = text.strip("```json").strip("```").strip()
            
            # Step 2: Parse the cleaned JSON string
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Parsing failed for text: {text}. Error: {e}")


def relationships(collection_name):



    relationships = {
        "users": {
            "collection": "users",
            "relation": "organizations",
            "related_field": "organizationId"
        },

        "companies": {
            "collection": "companies",
            "relation": "organizations",
            "related_field": "organizationId"
        },

        "proppant-delivery-entries": [{
            "collection": "proppant-delivery-entries",
            "relation": "organizations",
            "related_field": "organizationId"
        },
        {
            "collection": "proppant-delivery-entries",
            "relation": "jobs",
            "related_field": "jobId"
        }],

        "activity-log-entries": [{
            "collection": "activity-log-entries",
            "relation": "organizations",
            "related_field": "organizationId"
        },
        {
            "collection": "activity-log-entries",
            "relation": "jobs",
            "related_field": "jobId"
        }],

        "chemical-delivery-entries": [{
            "collection": "chemical-delivery-entries",
            "relation": "organizations",
            "related_field": "organizationId"
        },
        {
            "collection": "chemical-delivery-entries",
            "relation": "jobs",
            "related_field": "jobId"
        }],

        "field-tickets": [{
            "collection": "field-tickets",
            "relation": "organizations",
            "related_field": "organizationId"
        },
        {
            "collection": "field-tickets",
            "relation": "jobs",
            "related_field": "jobId"
        }],

        "on-site-equipments": [{
            "collection": "on-site-equipments",
            "relation": "organizations",
            "related_field": "organizationId"
        },
        {
            "collection": "on-site-equipments",
            "relation": "fleet",
            "related_field": "fleetId"
        }],
        
        "proposal-scheduler-v2": [{
            "collection": "proposal-scheduler-v2",
            "relation": "organizations",
            "related_field": "organizationId"
        },
        {
            "collection": "proposal-scheduler-v2",
            "relation": "fleet",
            "related_field": "fleetId"
        },
        {   
            "collection": "proposal-scheduler-v2",
            "relation": "districts",
            "related_field": "districtId"
        }],
    }


    return relationships.get(collection_name, [])



sample_aggregation = [
    {
        "$lookup": {
            "from": "organizations",
            "let": { "orgId": "$organizationId" },
            "pipeline": [
                {
                    "$match": {
                        "$expr": { "$eq": ["$_id", "$$orgId"] }
                    }
                }
            ],
            "as": "organizationDetails"
        }
    },
    { 
        "$unwind": "$organizationDetails" 
    },
    { 
        "$match": {
            "$expr": {
                "$eq": [
                    { "$toLower": "$organizationDetails.name" },
                    { "$toLower": "ProFrac" }
                ]
            }
        }
    },
    {
        "$project": {
            "firstName": 1,
            "lastName": 1,
            "userName": 1,
            "title": 1,
            "status": 1
        }
    }
]

# sample_aggregation = [
#     {
#         '$lookup': {
#             'from': 'organizations',
#             'let': { 'orgId': { '$toObjectId': '$organizationId' } },
#             'pipeline': [
#                 {
#                     '$match': {
#                         '$expr': { '$eq': ['$_id', '$$orgId'] }
#                     }
#                 }
#             ],
#             'as': 'organizationDetails'
#         }
#     },
#     { '$unwind': '$organizationDetails' },
#     { '$match': { 'organizationDetails.name': 'ProFrac' } },
#     {
#         '$project': {
#             'firstName': 1,
#             'lastName': 1,
#             'userName': 1,
#             'title': 1,
#             'status': 1
#         }
#     }
# ]


def count_tokens(input_text, output_text):

    tokenizer = tiktoken.encoding_for_model('gpt-4o')

    input_tokens = len(tokenizer.encode(input_text))
    output_tokens = len(tokenizer.encode(str(output_text)))
    total_tokens = input_tokens + output_tokens

    return {"input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens}