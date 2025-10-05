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

# llm = ChatOpenAI(    
#     model=config["mistral"]["name"],
#     openai_api_key=openai_token,
#     openai_api_base=config["mistral"]["url"],
#     max_tokens=512,
#     temperature=0,
#     http_client=cert_client
# )


from dotenv import load_dotenv  
import yaml
import os

from langchain_google_genai import ChatGoogleGenerativeAI

# Load env + config
load_dotenv()
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Use Gemini API key from env
gemini_api_key = "AIzaSyBO-UXBTE0FM7n_Vc1asu9T7Vf_pLw-Yks"

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",   # e.g., "gemini-1.5-pro" or "gemini-1.5-flash"
    google_api_key=gemini_api_key,
    temperature=0,
    max_output_tokens=512
)

