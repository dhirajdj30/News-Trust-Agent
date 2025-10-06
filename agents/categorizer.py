# from langchain_core.prompts import ChatPromptTemplate
# import json
# from db.insertion import save_category
# from llm_node import llm

# def json_formatter(llm_response):
#     import json
#     import re
#     # Regex to extract the first {...} block
#     match = re.search(r"\{.*\}", llm_response, re.DOTALL)
#     if match:
#         json_str = match.group()
#         data = json.loads(json_str)  # Convert to Python dict
#         return data                  # {'category': 'Seasonal', 'confidence': 0.95}
#     else:
#         print("No JSON found")

# def categorize_node(state):
#     """
#     LangGraph node: classify article and store in DB
#     state: {article_id, title, content}
#     """


#     article_id = state["article_id"]
#     title = state["title"]
#     content = state.get("content", "")

#     # article_id = 101
#     # title = "Heavy rains expected to boost umbrella sales in Mumbai"
#     # content = "Analysts suggest seasonal demand will drive short-term stock gains for umbrella companies."


#     prompt_template = """
#         You are a financial news classifier.
#         Task: Given a headline and article body, return the most relevant category.

#         Categories: Finance, Economy, Seasonal, Sports, Politics, Global, Other

#         Respond in JSON:
#         {{
#         "category": "<one of the categories>",
#         "confidence": <0.0 - 1.0>
#         }}

#         Title: {title}
#         Body: {body}
#     """

#     prompt = prompt_template.format(title=title, body=content)

#     response = llm.invoke(prompt)  # single step call
#     print("----------------LLM RESPONSE----------: ", response.content)
#     try:
#         result = json_formatter(response.content)
#         category = result["category"]
#         confidence = float(result["confidence"])
#     except Exception:
#         category, confidence = "Other", 0.0

#     # Save in Postgres
#     print("----------------article_id----------: ", article_id)
#     print("----------------LLM category----------: ", category)
#     print("----------------LLM confidence----------: ", confidence)
#     save_category(article_id, category, confidence)

#     return {"category": category, "confidence": confidence}


# if __name__ == "__main__":
#     categorize_node()

from langchain_core.prompts import ChatPromptTemplate
import json
import re
from db.insertion import save_category
from llm_node import llm


def json_formatter(llm_response: str):
    """
    Extracts JSON content from the LLM response text.
    """
    match = re.search(r"\{.*\}", llm_response, re.DOTALL)
    if match:
        try:
            json_str = match.group()
            return json.loads(json_str)  # Example: {'category': 'Finance', 'confidence': 0.9}
        except json.JSONDecodeError:
            print("⚠️ Failed to parse JSON.")
    else:
        print("⚠️ No JSON found in LLM response.")
    return {"category": "Other", "confidence": 0.0}


def categorize_node(state):
    """
    LangGraph node: classify an article using LLM and store result in DB.
    Input/Output: State object with fields (article_id, title, content, summary, etc.)
    """

    article_id = state.get("article_id", 101)


    print(f"🧠 Categorizing article ID: {article_id}")

    title = state.get("title", "No Title")
    content = state.get("content", "dummyyyyyyyyyyy")

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

    # Call the LLM
    response = llm.invoke(prompt)
    print("🧾 Raw LLM Response:", response.content)

    # Parse the LLM output
    result = json_formatter(response.content)
    category = result.get("category", "Other")
    confidence = float(result.get("confidence", 0.0))

    # Save category in the database
    save_category(article_id, category, confidence)
    print(f"✅ Saved category '{category}' (confidence: {confidence}) for article {article_id}")

    state["step"] = "categorize"
    print("-----------------------------------------")
    print(state)
    return state


# Optional standalone test
if __name__ == "__main__":
    from langgraph.graph import MessagesState

    class TestState(MessagesState):
        article_id: int = 101
        title: str = "Heavy rains expected to boost umbrella sales in Mumbai"
        content: str = "Analysts suggest seasonal demand will drive short-term stock gains for umbrella companies."
        summary: str = ""

    test_state = TestState()
    test_state["article_id"] = 101
    test_state["title"] = "Heavy rains expected to boost umbrella sales in Mumbai"
    test_state["content"] = "Analysts suggest seasonal demand will drive short-term stock gains for umbrella companies."

    updated_state = categorize_node(test_state)
    print("Updated State:", updated_state)

