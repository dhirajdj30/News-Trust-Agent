from db.vector_db import retrieve_articles
from db.fetch import fetch_article_by_id
from agents.categorizer import categorize_node

def fetch_relevant_articles(state):
    """
    LangGraph node: fetches the most relevant article based on the state's query.
    Updates the state with article_id, title, and content.
    """
    if not is_updated():
        from db.vector_db import store_in_vector_db
        from agents.rss_feed import ingest_all_feeds
        ingest_all_feeds()
        store_in_vector_db()
    query = state.get("query", "")
    print(f"🔎 Fetching relevant articles for query: {query}")

    # Retrieve articles using the vector database
    results = retrieve_articles(query, top_k=5)
    if not results:
        raise ValueError("No relevant articles found.")

    # Fetch full article details from DB
    for article_id in results:
        article = fetch_article_by_id(article_id)
        if article:
            article_id, title, content, url, published_at = article
            state["article_id"] = article_id
            state["title"] = title
            state["content"] = content
            categorize_node(state=state)  # Call categorization node
            print("-----------------------------------------")
            print(state)
            print(f"✅ Fetched Article ID: {article_id}, Title: {title}")
        else:
            raise ValueError(f"Article with ID {article_id} not found.")
        
    return state


# Optional: standalone test
if __name__ == "__main__":
    from langgraph.graph import MessagesState
    from agents.is_updated_db import is_updated

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

    state = TestState()
    state["query"] = "give me top 5 stocks to buy"
    updated_state = fetch_relevant_articles(state)
    print("Fetched Article:", updated_state)
