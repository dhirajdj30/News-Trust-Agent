import httpx
from langchain_openai import ChatOpenAI
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

def get_llm(max_tokens=512, temperature=0):
    ca_cert = config["mlflow"]["ops_bundle"]

    cert_client = httpx.Client(verify=ca_cert)

    return ChatOpenAI(    
        model=config["mistral"]["name"],
        openai_api_key="token-abc123",
        openai_api_base=config["mistral"]["url"],
        max_tokens=max_tokens,
        temperature=temperature,
        http_client=cert_client
    )


if __name__ == "__main__":
    llm = get_llm(10, 0.4)
    print(llm.invoke("What is the capital of France?"))