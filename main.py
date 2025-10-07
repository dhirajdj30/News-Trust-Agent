from langgraph.graph import StateGraph, START, END, MessagesState
from agents.fetch_article import fetch_relevant_articles
from agents.categorizer import categorize_node
from IPython.display import Image, display


# ✅ Define shared state model
class State(MessagesState):
    article_id: int | None = None
    query: str = "give me top 5 stocks to buy"
    title: str | None = None
    content: str | None = None
    summary: str = ""
    category: str | None = None
    confidence: float | None = None


if __name__ == "__main__":
    print("🚀 Building LangGraph workflow...")

    # ✅ Step 1: Build the graph structure
    graph = StateGraph(State)

    # Add nodes (functions)
    graph.add_node("fetch_relevant_articles", fetch_relevant_articles)
    graph.add_node("categorize", categorize_node)

    # Define edges (workflow order)
    graph.add_edge(START, "fetch_relevant_articles")
    graph.add_edge("fetch_relevant_articles", "categorize")
    graph.add_edge("categorize", END)

    # ✅ Step 2: Compile graph
    graph = graph.compile()

    # Optional visualization (if in Jupyter or IPython)
    try:
        display(Image(graph.get_graph().draw_mermaid_png()))
    except Exception:
        pass

    # ✅ Step 3: Run the workflow
    state = State(query="give me top 5 stocks to buy")
    print("🧭 Starting workflow with query:", state.query)

    result = graph.invoke(state)

    print("\n✅ Final Categorization Result:")
    print("--------------------------------")
    print(f"Article ID: {result.article_id}")
    print(f"Title: {result.title}")
    print(f"Category: {result.category}")
    print(f"Confidence: {result.confidence}")

