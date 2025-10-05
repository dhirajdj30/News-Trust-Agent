# from langchain_core.prompts import ChatPromptTemplate
import json
from db.insertion import save_category
from mlflow_client import mlflow_client
from llm_node import llm

mlflow_client()



def categorize_node():
    """
    LangGraph node: classify article and store in DB
    state: {article_id, title, content}
    """


    # article_id = state["article_id"]
    # title = state["title"]
    # content = state.get("content", "")

    article_id = 101
    title = "Heavy rains expected to boost umbrella sales in Mumbai"
    content = "Analysts suggest seasonal demand will drive short-term stock gains for umbrella companies."
    

    prompt_template = """
        You are a financial news classifier.
        Task: Given a headline and article body, return the most relevant category.

        Categories: Finance, Economy, Seasonal, Sports, Politics, Global, Other

        Respond in JSON:
        {{
        "category": "<one of the categories>",
        "confidence": <0.0 - 1.0>
        }}

        Title: {title}
        Body: {body}
    """

    prompt = prompt_template.format(title=title, body=content)

    response = llm.invoke(prompt)  # single step call
    print("----------------LLM RESPONSE----------: ", response.content)
    try:
        result = json.loads(response.content)
        category = result["category"]
        confidence = float(result["confidence"])
    except Exception:
        category, confidence = "Other", 0.0

    # Save in Postgres
    print("----------------article_id----------: ", article_id)
    print("----------------LLM category----------: ", category)
    print("----------------LLM confidence----------: ", confidence)
    save_category(article_id, category, confidence)

    return {"category": category, "confidence": confidence}


if __name__ == "__main__":
    categorize_node()