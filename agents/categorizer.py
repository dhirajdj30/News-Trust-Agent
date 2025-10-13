import json
import re
from db.insertion import save_category
from agents.llm_node import get_llm


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
    llm = get_llm()
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
    state["category"] = category
    state["confidence"] = confidence
    print(state)
    return state


# Optional standalone test
if __name__ == "__main__":
    from langgraph.graph import MessagesState

    class TestState(MessagesState):
        article_id: int | None = None
        query: str = "give me top 5 stocks to buy"
        title: str | None = None
        content: str | None = None
        category: str | None = None
        confidence: float | None = None
        summary: str | None = None
        step: str | None = None
        type: str | None = None

    test_state = TestState()
    test_state["article_id"] = 101
    test_state["title"] = "TCS share price falls after Q2 results. Should you buy or sell the large-cap IT stock?"
    test_state["content"] = "TCS share price has fallen over 2% in one month and more than 10% in three months. The largecap IT stock has declined 6% in six months and has dropped over 26% on a year-to-date (YTD) basis. Over the past one year, TCS share price has fallen 28% and it has declined 16% in two years."

    updated_state = categorize_node(test_state)
    print("Updated State:", updated_state)

