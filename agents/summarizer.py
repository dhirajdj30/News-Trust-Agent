from agents.llm_node import get_llm
import json
import re

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
    return {"type": "neutral", "summary": "Json Formarting Error"}

def summarize_article(state):
    print("📝 Summarizing article...")
    title = state.get("title", "No Title")
    content = state.get("content", "")

    prompt_template = """
        You are a financial news analyst AI that classifies market sentiment.
        Task: Given a stock-related news title and content, determine whether the overall tone is positive or negative for the stock market.
        Rules(Follow these strict rules):
        - 1. Read the title and content carefully and judge if the article implies confidence, optimism, profit growth, upgrades, expansion → bullish.
        - 2. Or if it implies risk, losses, downgrades, layoffs, regulation, slowdown → bearish.
        - 3. Then summarize the main reason for your sentiment in one or two short sentences.
        - 4. Output must be a **pure JSON object** only, no explanations, no markdown.

        Respond in JSON:
        {{
        "type": "positive" | "negative",
        "summary": "<short reasoned summary>"
        }}

        Title: {title}
        Body: {body}
        """

    prompt = prompt_template.format(title=title, body=content)
    llm = get_llm()
    response = llm.invoke(prompt)
    print("🧾 Raw LLM Response:", response.content)
    result = json_formatter(response.content)
    sentiment_type = result.get("type", "neutral")
    summary = result.get("summary", "No summary available.")
    print(f"✅ Summarization Result: Type={sentiment_type}, Summary={summary}")
    state["type"] = sentiment_type
    state["summary"] = summary
    state["step"] = "summarize"
    return state


# Optional standalone test
if __name__ == "__main__":
    from langgraph.graph import MessagesState
    # Sentiment analysis can be added similarly

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
    test_state["article_id"] = 501
    test_state["title"] = "Buy HDFC Bank; target of Rs 1,850: ICICI Securities"
    test_state["content"] = "ICICI Securities is bullish on HDFC Bank has recommended buy rating on the stock with a target price of Rs 1,850 in its research report dated April 21, 2024."
    
    result = summarize_article(test_state)
    print("Updated State:", result)

