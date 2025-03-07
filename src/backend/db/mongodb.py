from src.backend.config import MONGODB_URI, MONGODB_DB_NAME
from src.backend.utils import is_valid_epoch
from pymongo import MongoClient
from bson.json_util import dumps
from bson import ObjectId
from datetime import timezone, datetime
import json
import ast
import re

class MongoEngine:
    def __init__(self, uri: str = MONGODB_URI, db_name: str = MONGODB_DB_NAME):
        """
        Initialize the MongoDB connection.
        
        :param mongo_uri: Connection string for MongoDB.
        :param db_name: Name of the database to interact with.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.db_name = db_name
    

    def execute_query(self, state):
        """
        Execute a query on the specified collection and format the response.
        """
        try:

            if 'is_cached' in state.keys() and state['is_cached'] == True:
                query = state["mongo_query"] 
            else:
                query = state["mongo_query"].get('query')

            collection_name = state.get("collection_name")[0] if isinstance(state.get("collection_name"), list) else state.get("collection_name") 
            aggregate = state.get("aggregate")
            skip = state.get('skip', 0)
            limit = state.get('limit', 10000)

            collection = self.db[collection_name]
            # 1. **Run an explain() check first to validate the query**
            try:
                if not aggregate:
                    explain_plan = collection.find(query).explain()
                    print("MongoDB Query Plan:", explain_plan)  
                else:
                    self.db.command("aggregate", collection_name[0], pipeline=query, explain=True)
            except Exception:
                state['execution_status'] = False
                return state

            # 2. **Execute the actual query**
            if aggregate:
                results = list(collection.aggregate(query))
                total_items = len(list(collection.aggregate(query)))
            else:
                results = list(collection.find(query).skip(skip).limit(limit))
                total_items = len(list(collection.find(query)))

            # 3. **Differentiate between a valid empty result and an incorrect query**
            if results:  # Data found
                state['execution_status'] = True
                json_results = dumps(results)
                parsed_results = self.parse_data(data=json_results)
                columns = self.get_columns_from_sample(sample=parsed_results[0])

                response = {
                    "module": collection_name,
                    "columns": columns,
                    "results": parsed_results,
                    "total_items": total_items
                }

                state['data'] = response
            else:  # Query executed fine but returned no results
                state['execution_status'] = True  # Query executed successfully
                state['data'] = {
                    "module": collection_name,
                    "columns": [],
                    "results": [],
                    "total_items": 0
                }

            return {**state}

        except Exception as e:
            state['execution_status'] = False  # Query failed
            raise ValueError(f"Error while executing query on database: {e}")


        
    def parse_data(self,data):
        
        data = json.loads(data)

        fields_to_exclude = ["_id", "_class", "password", "modified", "created", "lastLogInTime", "ts", "jobId", "wellId", "proposalId", "organizationId", "fleetId","districtId", "modified", "curWellId","azureId","logoId"]

        for document in data:
            for field in fields_to_exclude:
                if field in document:
                    del document[field]

            date_fields = [date_field for date_field in document.keys() if 'date' in str(date_field).lower()]
            if date_fields:
                for date_field in date_fields:
                    if is_valid_epoch(str(document[date_field])):
                        try:
                            document[date_field] = datetime.fromtimestamp(document[date_field] / 1000, tz=timezone.utc)
                        except Exception as e:
                            print(f"Error processing field '{date_field}': {e}")
        
        results = []
        for obj in data:
            results.append({k: v for k, v in obj.items() if not isinstance(v, (dict, list, ObjectId))})

        return results
    
    def get_columns_from_sample(self, sample):
        """
        Format column names by sampling a subset of documents.
        
        :param sample: Sample to work with.
        :return: List of formatted objects.
        """
        try:
            formatted_list = []
            columns = [key for key in sample.keys()]
            
            for column in columns:
                words = re.sub('([a-z])([A-Z])', r'\1 \2', column).split('_')
                name = ' '.join([word[0].upper() + word[1:] for word in words])
                formatted_list.append({"name": name, "key": column})
            
            return formatted_list            

        except Exception as e:
            print(f"An error occurred: {e}")
            return set()
        

    
    def _get_collection_metadata(self, collection_name: str) -> dict:
        """
        Retrieves metadata for a specific collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            dict: A dictionary containing the collection name and its fields with data types.
        """
        collection = self.db[collection_name]
        sample_doc = collection.find_one()
        fields = {}
        if sample_doc:
            for field, value in sample_doc.items():
                fields[field] = type(value).__name__
        else:
            print(f"Collection '{collection_name}' is empty.")

        return {
            'collection_name': collection_name,
            'fields': fields,
        }
    
    def fetch_prev_data(self):
        collection = self.db['queries']