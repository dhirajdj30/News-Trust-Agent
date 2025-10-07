from agents.llm_node import get_llm

def controller_node(state):
    """
    LLM orchestrator — decides what to do next.
    """
    print("🤖 Controller deciding next step...")

    # Tell the LLM about available tools
    system_prompt = """
    You are the workflow controller for a financial news agent.
    You can use these tools:
    - fetch_relevant_articles: to get the latest news
    - categorize_article: to classify the news
    - summarize_article: to generate a short summary

    You will decide the next tool to call based on the user's query and the current state.
    Respond only in JSON:
    { "next_step": "<tool_name>" }
    """

    # context = f"Current state:\n{state.model_dump_json(indent=2)}"
    full_prompt = system_prompt 

    llm = get_llm()
    response = llm.invoke(full_prompt)

    import json, re
    match = re.search(r"\{.*\}", response.content, re.DOTALL)
    if not match:
        print("⚠️ Could not parse controller response, defaulting to 'fetch_relevant_articles'")
        next_step = "fetch_relevant_articles"
    else:
        data = json.loads(match.group())
        next_step = data.get("next_step", "fetch_relevant_articles")

    print(f"🧭 Controller chose: {next_step}")
    state["step"] = next_step
    return state
