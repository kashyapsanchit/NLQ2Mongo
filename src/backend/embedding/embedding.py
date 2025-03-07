import logging
from supabase import create_client, Client
# from sentence_transformers import SentenceTransformer
from src.backend.config import SUPABASE_KEY, SUPABASE_URL
from src.ai.config import EMBEDDING_ENDPOINT, AZURE_OPENAI_API_KEY
from openai import AzureOpenAI

logging.basicConfig(level=logging.INFO)

class Embedding:
    def __init__(self):
        """Initialize the Supabase client and embedding model."""
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.azure_client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=EMBEDDING_ENDPOINT,
        )
        # self.model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1') # Change to ada

    def generate_embeddings(self, data: str):
        try:
            if isinstance(data, str):
                response = self.azure_client.embeddings.create(model="text-embedding-ada-002", input=[data])
                return response.data[0].embedding
            else:
                logging.info("Embedding generation failed : Input must be a string or a list of strings")
        except Exception as e:
            logging.error(f"Error generating embeddings: {str(e)}")
            return []


    def store_embeddings(self, data: dict) -> dict:
        """
        Store generated embeddings in the Supabase database.
        Returns the response from Supabase.
        """
        try:
            embeddings = self.generate_embeddings(data['user_input'])

            if not embeddings:
                raise ValueError("Failed to generate embeddings.")

            response = self.client.table("queries").insert({
                "query": data['query'],
                "user_input": data['user_input'],
                "embedding": embeddings,
                "collection_name": data['collection_name'],
                "aggregate": data['aggregate']
            }).execute()

            if response.data:
                logging.info("Embedding successfully stored in database.")
            return response
        except Exception as e:
            logging.error(f"Error storing embeddings: {str(e)}")
            return {"error": str(e)}

    def get_similar(self, user_input: str, top_k: int = 5) -> list | dict:
        """
        Fetch similar queries from Supabase using vector search.
        """
        try:
            user_embedding = self.generate_embeddings(user_input)

            if not user_embedding:
                raise ValueError("Failed to generate query embedding.")

            response = self.client.rpc("match_queries", {
                "query_embedding": user_embedding,
                "match_threshold": 0.8,
                "match_count": top_k
            }).execute()
            import pdb; pdb.set_trace()

            if response.data:
                return response.data[0]
            else:
                logging.warning("No similar queries found.")
                return False
        except Exception as e:
            logging.error(f"Error fetching similar queries: {str(e)}")
            return {"error": str(e)}

    # def generate_embeddings(self, data: str):
    #     """
    #     Generate embeddings for input text.
    #     Supports both single string and list of strings.
    #     """
    #     try:
    #         if isinstance(data, str):
    #             embedding = self.model.encode(data).tolist()
    #             return embedding
    #         else:
    #             raise ValueError("Input must be a string or a list of strings")
    #     except Exception as e:
    #         logging.error(f"Error generating embeddings: {str(e)}")
    #         return []