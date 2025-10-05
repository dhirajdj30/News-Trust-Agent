from dotenv import load_dotenv
import yaml
import os

from langchain_google_genai import ChatGoogleGenerativeAI

# Load env + config
# load_dotenv()
# with open("config.yaml") as f:
#     config = yaml.safe_load(f)

# Use Gemini API key from env
gemini_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",   # e.g., "gemini-1.5-pro" or "gemini-1.5-flash"
    google_api_key=gemini_api_key,
    temperature=0,
    max_output_tokens=512
)