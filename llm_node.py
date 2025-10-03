from langchain_openai import ChatOpenAI
from dotenv import load_dotenv  
import httpx
import yaml
import os

load_dotenv()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

openai_token= os.getenv("openai_token")
ops_bundle_path = config["mlflow"]["ops_bundle"]
cert_client = httpx.Client(verify=ops_bundle_path)

llm = ChatOpenAI(    
    model=config["mistral"]["name"],
    openai_api_key=openai_token,
    openai_api_base=config["mistral"]["url"],
    max_tokens=512,
    temperature=0,
    http_client=cert_client
)

