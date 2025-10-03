# 📰 News Trust Agent

**News Trust Agent** is an **agentic Python application** built with [uv](https://github.com/astral-sh/uv) that helps evaluate the **trustworthiness of financial news sources**.

It ingests news from sources like Moneycontrol, CNBC, Bloomberg, etc., categorizes the news (Finance, Seasonal, Sports, etc.), and assigns ratings to news providers **based on category performance over time**.

💡 Example:

* If “heavy rain” news → Umbrella company stock goes up → Seasonal category
* If “India wins cricket match” → Jersey company stock rises → Sports category
* Over time, sources like Moneycontrol or CNBC are rated based on how accurate they are in each category.

---

## 🚀 Features

* 📥 **Fetch RSS feeds** from multiple financial news sources
* 🧠 **Agentic pipeline (LangGraph + LLMs)** to:

  * Classify news into categories
  * Extract events and stock impact
  * Generate **top 5 stock predictions**
* 📊 **Database-backed rating system**:

  * Source ratings by category
  * Updates ratings using **T+1 feedback loop** (after outcome is known)
* 🔄 **Feedback loop** to refine source credibility over time

---

## 📂 Project Structure

```
.
├── db/                # Database utilities & migrations
├── agents/            # Agent definitions (LangGraph nodes)
├── prompts/           # LLM prompt templates
├── app.py             # Main entrypoint for the application
├── rss_feed.py        # Fetch RSS feeds from news providers
├── rssfeeds.csv       # List of RSS feeds (sources)
└── README.md          # This file
```

---

## 🛠️ Setup

### 1. Install dependencies

This project uses [uv](https://docs.astral.sh/uv/) for Python project management.

```bash
uv venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
uv sync
```

### 2. Configure RSS feeds

Edit `rssfeeds.csv` to add/remove sources. Example:

```csv
source_name,source_url,category
Moneycontrol,https://www.moneycontrol.com/rss/latestnews.xml,Finance
CNBC,https://www.cnbc.com/id/100003114/device/rss/rss.html,Finance
```

---

## ▶️ Usage

### Run the agent

```bash
python rss_feeds.py
```

This will:

1. Stores latest news to `rssfeeds.csv`

### Add a new agent

Add a new Python file under `/agents` and register it in `app.py`.

---

## 📊 Feedback Loop

Predictions are evaluated after **1 trading day (T+1)**:

* Correct → Increases source rating
* Wrong → Decreases source rating
* Partial → Small adjustment

This way, the system **learns which sources are more reliable** in each category.

---

## 🧩 Roadmap

* [ ] Add more RSS/news sources
* [ ] Streamlit/FastAPI dashboard for predictions & ratings
* [ ] Replace LLM categorization with FinBERT model

---

## 🤝 Contributing

PRs are welcome! Please open an issue for discussion before submitting major changes.

---