from dotenv import load_dotenv
import os

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')
OPENAI_API_TYPE = os.getenv('OPENAI_API_TYPE', 'azure')
OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION', '')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', '')
AZURE_DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT_NAME', '')
EMBEDDING_ENDPOINT = os.getenv('EMBEDDING_ENDPOINT', '')
COLLECTIONS = os.getenv('COLLECTIONS')