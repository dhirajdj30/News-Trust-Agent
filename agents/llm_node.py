from dotenv import load_dotenv
import yaml
import os

# from langchain_google_genai import ChatGoogleGenerativeAI

# Load env + config
load_dotenv()
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# # Use Gemini API key from env
# gemini_api_key = os.getenv("GOOGLE_API_KEY")

# # Initialize Gemini LLM
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",   # e.g., "gemini-1.5-pro" or "gemini-1.5-flash"
#     google_api_key=gemini_api_key,
#     temperature=0,
#     max_output_tokens=512
# )


import httpx
from langchain_openai import ChatOpenAI

# Load env + config
load_dotenv()
with open("config.yaml") as f:
    config = yaml.safe_load(f)

def get_llm():
    ca_cert = config["mlflow"]["ops_bundle"]    

    cert_client = httpx.Client(verify=ca_cert)
    mistral = config["mistral"]

    return ChatOpenAI(    
        model=mistral["name"],
        openai_api_key="token-abc123",
        openai_api_base=mistral["url"],
        max_tokens=512,
        temperature=0,
        http_client=cert_client
    )
