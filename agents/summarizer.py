from llm_node import llm

def summarize_article(state):
    print("📝 Summarizing article...")
    content = state.get("content", "")
    prompt = f"Summarize the following article briefly:\n\n{content}"
    response = llm.invoke(prompt)
    state["summary"] = response.content.strip()
    state["step"] = "summarize"
    return state