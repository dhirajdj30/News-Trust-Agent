from agents.llm_node import get_llm

def summarize_article(state):
    print("📝 Summarizing article...")
    content = state.get("content", "")
    prompt = f"Summarize the following article briefly:\n\n{content}"
    llm = get_llm()
    response = llm.invoke(prompt)
    state["summary"] = response.content.strip()
    state["step"] = "summarize"
    return state


# Optional standalone test
if __name__ == "__main__":
    from langgraph.graph import MessagesState

    # Dummy state for testing
    state = MessagesState(content="This is a long article about financial markets and investment strategies...")
    result = summarize_article(state)
    print("Summary:", result["summary"])