from db.vector_db import retrieve_articles
from db.fetch import fetch_article_by_id

def fetch_relevant_articles(state):
    """
    LangGraph node: fetches the most relevant article based on the state's query.
    Updates the state with article_id, title, and content.
    """

    query = state.get("query", "")
    print(f"🔎 Fetching relevant articles for query: {query}")

    # Retrieve articles using the vector database
    results = retrieve_articles(query, top_k=5)
    if not results:
        raise ValueError("No relevant articles found.")

    # # Take the first article metadata
    # article_id = results[0]

    # Fetch full article details from DB
    for article_id in results:
        article = fetch_article_by_id(article_id)
        if article:
            article_id, title, content, url, published_at = article
            state["article_id"] = article_id
            state["title"] = title
            state["content"] = content
            print(f"✅ Fetched Article ID: {article_id}, Title: {title}")
        else:
            raise ValueError(f"Article with ID {article_id} not found.")

    state["step"] = "fetch_relevant_articles"
    print("-----------------------------------------")
    print(state["article_id"])
    return state


# Optional: standalone test
if __name__ == "__main__":
    from langgraph.graph import MessagesState

    class TestState(MessagesState):
        article_id: int | None = None
        query: str = "give me top 5 stocks to buy"
        title: str | None = None
        content: str | None = None
        summary: str = ""

    state = TestState()
    state["query"] = "give me top 5 stocks to buy"
    updated_state = fetch_relevant_articles(state)
    print("Fetched Article:", updated_state)
