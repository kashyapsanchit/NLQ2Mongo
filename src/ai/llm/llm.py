from langchain_openai.chat_models import AzureChatOpenAI
from src.ai.config import AZURE_DEPLOYMENT_NAME, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, OPENAI_API_TYPE, OPENAI_API_VERSION


def llm():

    llm = AzureChatOpenAI(
    openai_api_type=OPENAI_API_TYPE,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    openai_api_version=OPENAI_API_VERSION,
    deployment_name=AZURE_DEPLOYMENT_NAME,
    openai_api_key=AZURE_OPENAI_API_KEY
    )

    return llm 

