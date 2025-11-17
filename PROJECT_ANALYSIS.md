# 📰 News-Trust-Agent: Comprehensive Project Analysis

## 🎯 Project Overview

**News-Trust-Agent** is the **real-time news sentiment agent** component of your larger **Unified Stock Intelligence (USI)** system. This is a specialized agentic Python application built with **LangGraph** that evaluates financial news sources' trustworthiness through an intelligent feedback loop mechanism.

**Core Mission**: Ingest financial news from multiple RSS feeds, categorize articles using LLM, and build a dynamic rating system that tracks source credibility over time based on prediction outcomes.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   News Trust Agent System                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. DATA INGESTION LAYER                                     │
│     ├─ RSS Feed Fetching (rss_feed.py)                       │
│     ├─ Multiple Sources: Moneycontrol, LiveMint, Investing   │
│     └─ Article Storage in PostgreSQL                         │
│                                                               │
│  2. VECTOR DATABASE LAYER                                    │
│     ├─ FAISS-based Semantic Search (vector_db.py)            │
│     ├─ Sentence Transformer Embeddings (all-MiniLM-L6-v2)   │
│     └─ Similarity-based Article Retrieval                    │
│                                                               │
│  3. AGENTIC WORKFLOW LAYER (LangGraph)                       │
│     ├─ Fetch Relevant Articles Node                          │
│     ├─ Categorizer Node (LLM-based Classification)           │
│     ├─ Summarizer Node                                       │
│     └─ Controller Node (Orchestrator)                        │
│                                                               │
│  4. LLM LAYER                                                │
│     └─ Google Gemini 2.5 Flash Model                         │
│                                                               │
│  5. DATABASE LAYER                                           │
│     ├─ PostgreSQL (Relational Data)                          │
│     ├─ FAISS (Vector Store)                                  │
│     └─ MLFlow (Experiment Tracking)                          │
│                                                               │
│  6. FEEDBACK & RATING LAYER                                  │
│     ├─ Source Rating Updates (news_rating.py)                │
│     ├─ T+1 Feedback Loop                                     │
│     └─ Dynamic Credibility Scoring                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Component Deep Dive

### 1. **Data Ingestion Pipeline** (`rss_feed.py` & `agents/rss_feed.py`)

#### Purpose
Continuously fetch financial news from multiple RSS feeds and store them in PostgreSQL.

#### Key Features
- **Multi-Source RSS Aggregation**:
  - Moneycontrol (1 feed)
  - LiveMint (2 feeds: money + markets)
  - Investing.com (4 feeds: stocks, picks, news)
  - Business Standard (1 feed)

- **Article Processing**:
  - HTML stripping via BeautifulSoup
  - Deduplication (URL-based)
  - Metadata extraction (title, link, published_at, summary)

- **Data Flow**:
  ```
  RSS URL → feedparser → Extract entry → Clean HTML → Insert to DB
  ```

#### Current Implementation Status
✅ **Complete**: RSS feeds configured and ingestion logic ready
⚠️ **TODO**: Schedule periodic ingestion (currently manual call only)

---

### 2. **Database Layer** (`db/` directory)

#### Schema Architecture

**`news_sources`** - News provider registry
```sql
source_id (PK) | source_name | source_url
```

**`categories`** - Article classification categories
```sql
category_id (PK) | category_name
-- Finance, Economy, Seasonal, Sports, Politics, Global, Tech, M&A, SupplyChain, Other
```

**`news_articles`** - Article storage
```sql
article_id | source_id (FK) | title | content | url | published_at | 
category_id (FK) | llm_confidence | inserted_at
```

**`news_ratings`** - Dynamic source credibility scores
```sql
rating_id | source_id (FK) | category_id (FK) | rating (0-10) | 
rating_count | last_updated
```

**`predictions`** - Agent's stock predictions
```sql
prediction_id | source_id (FK) | category_id (FK) | stock_symbol | 
predicted_at | target_date | outcome (Pending/Correct/Wrong/Partial)
```

**`feedback`** - T+1 outcome validation
```sql
feedback_id | prediction_id (FK) | user_id | outcome | rating | feedback_time
```

**`prediction_sources`** - Lineage tracking
```sql
id | prediction_id (FK) | source_id (FK) | article_url | article_title | 
source_rating | llm_confidence | weight
```

**`agent_logs`** - Audit trail
```sql
log_id | event_time | node_name | message (JSONB)
```

#### Key Files

| File | Purpose |
|------|---------|
| `connection.py` | PostgreSQL connection manager (uses .env for credentials) |
| `creation.py` | Schema initialization script |
| `insertion.py` | Article & category insertion functions |
| `fetch.py` | Query functions (fetch_table, fetch_todays_articles, fetch_article_by_id) |

#### Status
✅ **Complete**: Schema designed with comprehensive relationships
✅ **Complete**: All CRUD operations implemented
⚠️ **TODO**: Add indexes for performance optimization

---

### 3. **Vector Database & Semantic Search** (`db/vector_db.py`)

#### Purpose
Enable semantic similarity search to retrieve contextually relevant articles based on user queries.

#### Implementation
- **Embedding Model**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
  - Lightweight (~80MB)
  - Fast inference
  - Good semantic representation for financial text

- **Vector Store**: FAISS (Facebook AI Similarity Search)
  - In-memory local index
  - Fast approximate nearest neighbor search
  - Persisted to `./vector_store/faiss_index`

#### Key Functions
```python
store_in_vector_db()
  ├─ Fetches today's articles from PostgreSQL
  ├─ Generates embeddings for title + content
  ├─ Stores in FAISS with metadata
  └─ Saves index locally

retrieve_articles(query, top_k=5)
  ├─ Loads FAISS index
  ├─ Computes embedding of query
  ├─ Returns top-k similar article IDs
  └─ Prints retrieved article summaries
```

#### Workflow
```
User Query → Sentence Transformer → Embedding Vector
                                         ↓
                                    FAISS Index
                                         ↓
                          Top-5 Similar Articles (by ID)
                                         ↓
                          Fetch Full Article Details
```

#### Status
✅ **Complete**: Semantic search working
✅ **Complete**: Daily article ingestion
⚠️ **TODO**: Implement incremental index updates (currently full recompute)

---

### 4. **LLM Integration** (`llm_node.py`)

#### Model Configuration
- **Provider**: Google Generative AI (Gemini)
- **Model**: `gemini-2.5-flash` (latest, fast, cost-effective)
- **Temperature**: 0 (deterministic output)
- **Max Tokens**: 512 (sufficient for JSON responses)
- **Auth**: API key from `.env` → `GOOGLE_API_KEY`

#### Implementation
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_api_key,
    temperature=0,
    max_output_tokens=512
)
```

#### Status
✅ **Complete**: LLM integration working
✅ **Complete**: API key management via .env
⚠️ **TODO**: Add error handling for API failures
⚠️ **TODO**: Implement retry logic & rate limiting

---

### 5. **Agentic Workflow** (`agents/` directory)

#### Overview
Uses **LangGraph** to orchestrate a multi-step workflow where different agents (nodes) specialize in specific tasks.

#### Agent Nodes

##### **A. Fetch Relevant Articles Node** (`fetch_article.py`)
**Role**: Retrieve the most contextually relevant articles for the user's query

**Input State**:
```python
query: str = "give me top 5 stocks to buy"
```

**Process**:
1. Invoke `retrieve_articles(query, top_k=5)` from vector DB
2. Take the first (most similar) article ID
3. Fetch full article details from PostgreSQL
4. Populate state with `article_id`, `title`, `content`

**Output State**:
```python
article_id: int
title: str
content: str
step: "fetch_relevant_articles"
```

**Status**: ✅ Complete & tested

---

##### **B. Categorizer Node** (`categorizer.py`)
**Role**: Classify article into financial categories using LLM

**Input State**:
```python
article_id: int
title: str
content: str
```

**Process**:
1. Build prompt with title & content
2. Call Gemini LLM with JSON-formatted request
3. Parse JSON response using regex
4. Extract `category` and `confidence` (0-1)
5. Save results to PostgreSQL `categories` & `news_articles` tables

**LLM Prompt Template**:
```
You are a financial news classifier.
Task: Given a headline and article body, return the most relevant category.

Categories: Finance, Economy, Seasonal, Sports, Politics, Global, Other

Respond in JSON:
{
  "category": "<one of the categories>",
  "confidence": <0.0 - 1.0>
}

Title: {title}
Body: {body}
```

**Output State**:
```python
category: str
confidence: float
step: "categorize"
```

**Status**: ✅ Complete & tested with JSON parsing

---

##### **C. Summarizer Node** (`summarizer.py`)
**Role**: Generate concise article summaries for downstream processing

**Input State**:
```python
content: str
```

**Process**:
1. Prompt LLM to summarize the article content
2. Update state with summary

**Output State**:
```python
summary: str
step: "summarize"
```

**Status**: ✅ Basic implementation complete

---

##### **D. Controller Node** (`controller.py`)
**Role**: LLM-based orchestrator that decides workflow sequence

**Process**:
1. Describe available tools (fetch, categorize, summarize)
2. Ask LLM "What should we do next?"
3. Parse JSON response for next step
4. Return next_step decision

**Supported Tools**:
- `fetch_relevant_articles`
- `categorize_article`
- `summarize_article`

**Status**: ✅ Basic implementation (needs refinement for actual routing)

---

#### Workflow Graph Definition (`main.py` and `notebook.ipynb`)

**Current Graph Structure**:
```
                         START
                           ↓
                    Controller Node
                      ↙  ↓  ↘
            fetch    cat   summ
              ↓      ↓      ↓
            Article Cat   Summ
              ↓      ↓      ↓
              └──→ Controller ←─┘
                      ↓
                      END
```

**State Model** (LangGraph MessagesState):
```python
class State(MessagesState):
    query: Annotated[list, add_messages]  # Supports multiple message additions
    article_id: int | None
    title: str | None
    content: str | None
    category: str | None
    confidence: float | None
    summary: str | None
    step: str | None  # Track which node last ran
```

**Status**: 
✅ Graph structure working
⚠️ **TODO**: Make controller routing logic deterministic (not fully random)
⚠️ **TODO**: Add conditional edges instead of routing to all nodes

---

### 6. **Feedback & Rating System** (`news_rating.py`)

#### Purpose
Implement T+1 feedback loop to dynamically adjust source credibility based on prediction outcomes.

#### Rating Algorithm (Bayesian-style)

**Outcome Scoring**:
```python
OUTCOME_SCORES = {
    "Correct": 10,    # Prediction was accurate
    "Partial": 5,     # Partially correct
    "Wrong": 0        # Incorrect prediction
}
```

**Update Formula**:
```
alpha = 1 / (1 + rating_count)              # Learning rate (adaptive)
new_rating = old_rating * (1 - alpha) + feedback_score * alpha
new_rating_count = rating_count + 1
```

**Key Properties**:
- **Older sources adapt slower** (high rating_count → low alpha)
- **New sources adapt faster** (low rating_count → high alpha)
- **Incremental update** (avoids full recomputation)
- **Bounded between 0-10**

#### Implementation
```python
def update_news_rating(prediction_id, feedback_outcome, star_rating=None):
    # 1. Get source_id, category_id from prediction
    # 2. Compute feedback_score (outcome + optional star rating)
    # 3. Fetch current rating & rating_count
    # 4. Apply Bayesian update formula
    # 5. Update database
```

#### Status
✅ **Concept complete** (documented in code)
⚠️ **TODO**: Integrate into actual prediction workflow
⚠️ **TODO**: Implement T+1 scheduler (check predictions 1 day later)

---

### 7. **Experiment Tracking** (`mlflow_client.py`)

#### Purpose
Track ML experiments, model performance, and agent behavior over time.

#### Implementation
- **MLFlow Tracking URI**: `http://127.0.0.1:5000` (local server)
- **Experiment Name**: `Agentic_Learning`
- **Auto-logging**: LangChain integration enabled

#### Setup Function
```python
def mlflow_client():
    client = MlflowClient(tracking_uri="http://127.0.0.1:5000")
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    exp_name = "Agentic_Learning"
    
    if mlflow.get_experiment_by_name(exp_name) is None:
        mlflow.create_experiment(name=exp_name)
    mlflow.set_experiment(exp_name)
    mlflow.langchain.autolog()
    
    return client
```

#### Status
✅ **Complete**: MLFlow integration ready
⚠️ **TODO**: Add custom metrics logging (article classification accuracy, etc.)
⚠️ **TODO**: Track source rating evolution over time

---

### 8. **Prompt Engineering** (`prompts/prompt.yaml`)

#### Prompts Defined

**Categorization Prompt**:
```
Input: Article title + content
Output: JSON with category, category_confidence (0-1), short_reason
Categories: Finance, Seasonal, Sports, Politics, Tech, Company, M&A, SupplyChain, Other
```

**Event Extraction Prompt** (for future):
```
Input: Article
Output: JSON array of market-relevant events
Fields: event_summary, affected_industries, implied_signal (±/neutral), confidence
```

**Prediction Prompt** (for future):
```
Input: Weighted articles from multiple sources
Output: Top-5 stocks to buy
Fields: symbol, rationale, confidence_score
```

#### Weighting Algorithm (Specified but not yet implemented):
```
weight = source_rating_normalized × llm_confidence × recency_factor

recency_factor = exp(-0.05 × hours_since_published)
source_rating_normalized = rating / 10
```

#### Status
✅ **Complete**: Prompts designed
⚠️ **TODO**: Implement event extraction node
⚠️ **TODO**: Implement prediction aggregation node with weighted voting

---

## 📦 Dependencies & Stack

### Key Libraries
```
langchain>=0.3.27                    # LLM framework
langgraph>=0.6.8                     # Agentic workflows
langchain-google-genai>=2.0.10       # Gemini API
sentence-transformers>=5.1.1         # Embeddings
faiss-cpu>=1.12.0                    # Vector search
psycopg2-binary>=2.9.10              # PostgreSQL driver
feedparser>=6.0.12                   # RSS parsing
beautifulsoup4>=4.14.2               # HTML parsing
mlflow==3.2.0                        # Experiment tracking
```

### Infrastructure
- **Database**: PostgreSQL (relational + metadata)
- **Vector Store**: FAISS (semantic search)
- **LLM**: Google Gemini 2.5 Flash
- **Experiment Tracking**: MLFlow (local)

---

## 🔄 Current Workflow Example

```
User Query: "give me top 5 stocks to buy"
│
├─→ [Fetch Node]
│   ├─ Query: "give me top 5 stocks to buy"
│   ├─ FAISS retrieval: article_id=123
│   └─ State: {query, article_id=123, title, content}
│
├─→ [Categorizer Node]
│   ├─ Input: title + content
│   ├─ LLM Call: "What category is this?"
│   ├─ Output: category="Finance", confidence=0.95
│   └─ DB Save: article_id→categories table
│
├─→ [Summarizer Node]
│   ├─ Input: content
│   ├─ LLM Call: "Summarize this"
│   ├─ Output: summary="..."
│   └─ State: {summary}
│
└─→ [Controller Node]
    ├─ Decision: "Should we continue?"
    └─ Output: step="END" or continue loop
```

---

## ✅ Completed Features

| Feature | Status | Location |
|---------|--------|----------|
| RSS Feed Ingestion | ✅ | `rss_feed.py`, `agents/rss_feed.py` |
| PostgreSQL Schema | ✅ | `db/schema.sql`, `db/creation.py` |
| Article Storage | ✅ | `db/insertion.py` |
| Semantic Search (FAISS) | ✅ | `db/vector_db.py` |
| LLM Integration (Gemini) | ✅ | `llm_node.py` |
| Article Categorization | ✅ | `agents/categorizer.py` |
| Article Summarization | ✅ | `agents/summarizer.py` |
| Agentic Workflow (LangGraph) | ✅ | `main.py`, `notebook.ipynb` |
| MLFlow Integration | ✅ | `mlflow_client.py` |
| Rating Algorithm Design | ✅ | `news_rating.py` (documented) |
| Prompt Engineering | ✅ | `prompts/prompt.yaml` |

---

## ⚠️ In-Progress / TODO

### High Priority
1. **T+1 Feedback Loop Integration**
   - [ ] Schedule daily evaluation of predictions
   - [ ] Update source ratings based on outcomes
   - [ ] Implement `update_news_rating()` function call in workflow

2. **Stock Prediction Node**
   - [ ] Create aggregation node to combine weighted articles
   - [ ] Implement voting mechanism for stock recommendations
   - [ ] Generate top-5 stock list with rationales

3. **Controller Routing Logic**
   - [ ] Make controller decisions deterministic based on state
   - [ ] Implement conditional edges (if categorized → else summarize)
   - [ ] Add termination conditions

4. **Event Extraction Node**
   - [ ] Parse articles for market-relevant events
   - [ ] Extract affected industries & signal direction
   - [ ] Store events for analysis

### Medium Priority
5. **Performance Optimization**
   - [ ] Add database indexes (article_id, published_at, category_id)
   - [ ] Implement incremental FAISS updates (avoid full rebuild)
   - [ ] Batch article processing

6. **Error Handling & Resilience**
   - [ ] Graceful handling of LLM API failures
   - [ ] Retry logic with exponential backoff
   - [ ] Dead letter queue for failed articles

7. **Advanced Features**
   - [ ] Multi-model ensemble for categorization
   - [ ] Fine-tuned embeddings on financial vocabulary
   - [ ] Entity linking (stocks mentioned in articles)
   - [ ] Sentiment analysis per source

### Lower Priority
8. **Monitoring & Observability**
   - [ ] Detailed agent logs with JSONB tracking
   - [ ] Metrics dashboard (articles/day, categorization accuracy, etc.)
   - [ ] Alert thresholds for anomalies

9. **Deployment**
   - [ ] Docker containerization
   - [ ] Scheduled task runner (Airflow, Celery)
   - [ ] REST API wrapper for external consumers

---

## 🎓 Architecture Decisions & Design Patterns

### 1. **Semantic Search with FAISS**
- **Why**: Fast, approximate nearest neighbor search (O(1) inference)
- **Trade-off**: Approximate vs exact matching (acceptable for news)
- **Future**: Could upgrade to hybrid BM25 + semantic for better recall

### 2. **LangGraph State Machine**
- **Why**: Composable, observable, and easy to debug agent workflows
- **Trade-off**: Verbose vs imperative code (worth for auditability)
- **Future**: Could add branching logic based on classification confidence

### 3. **Bayesian Rating Updates**
- **Why**: Source credibility adapts intelligently to new evidence
- **Trade-off**: Requires careful alpha tuning (learning rate)
- **Future**: Could use exponential moving average or Kalman filtering

### 4. **PostgreSQL + FAISS Dual Storage**
- **Why**: Relational for structured queries, FAISS for similarity
- **Trade-off**: Data consistency between two systems
- **Future**: Could use pgvector extension for unified storage

### 5. **Gemini Flash Model**
- **Why**: Fast, cheap, and good for structured JSON outputs
- **Trade-off**: Less capable than Pro models
- **Future**: Could use Pro for complex reasoning, Flash for routing

---

## 📊 Data Flow Diagram

```
                    RSS Feeds
                       │
                       ▼
            ┌─── Feedparser ───┐
            │  (parse + clean)  │
            └────────┬──────────┘
                     ▼
         ┌─── PostgreSQL (news_articles) ───┐
         │  - title, content, url, etc      │
         └────────┬──────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   Embeddings         Direct Query
        │                   │
        ▼                   ▼
   ┌─ FAISS ─┐        ┌────────────┐
   │ (vector) │        │  LangGraph │
   └────┬─────┘        │  Workflow  │
        │              └────────────┘
        ▼                   ▼
   Semantic Search    ┌──────────────┐
        │             │  Fetch Node  │
        └────┬────────│ Categorize   │
             │        │ Summarize    │
             └───────▶│ Controller   │
                      └──────────────┘
                             │
                             ▼
                      ┌────────────┐
                      │ LLM (Gemini)│
                      └────────────┘
                             │
                             ▼
                      ┌────────────┐
                      │  DB Update │
                      │ (ratings,  │
                      │ categories)│
                      └────────────┘
```

---

## 🔐 Environment Configuration

Required `.env` variables:
```bash
GOOGLE_API_KEY=<your-gemini-api-key>
dbname=<postgres-db-name>
user=<postgres-username>
password=<postgres-password>
host=localhost  # or your db host
port=5432
```

---

## 🚀 Next Steps for USI Integration

### Phase 1: Complete Real-Time News Agent
1. Implement stock prediction node (generate top-5 list)
2. Integrate T+1 feedback loop
3. Add event extraction for market catalysts

### Phase 2: Integrate with Technical Analysis Agent
1. Define data exchange format (article → stock symbol + signal)
2. Build integration API
3. Test with sample queries

### Phase 3: Integrate with Fundamental Analysis Agent
1. Combine ratings with financial metrics
2. Build decision ensemble
3. Generate final Buy/Hold/Sell recommendation

### Phase 4: End-to-End USI System
1. Build unified API
2. Add explanation generation (why we recommend this stock?)
3. Deploy and monitor

---

## 💡 Key Insights & Observations

1. **Well-Architected Foundation**: The project demonstrates solid understanding of LLM workflows, agentic patterns, and data engineering.

2. **Production-Ready Components**: Database schema, RSS ingestion, and LLM integration are well-designed.

3. **Extensibility**: The controller pattern and node-based architecture makes it easy to add new agents.

4. **Learning System**: The Bayesian rating update creates a self-improving credibility system—sources that consistently make good predictions gain trust over time.

5. **Transparency**: The `prediction_sources` table enables full lineage tracking (which articles influenced which predictions).

---

## 📝 Code Quality Notes

✅ **Strengths**:
- Clean separation of concerns (agents, DB, LLM)
- Good error handling with try-catch
- Descriptive variable names and comments
- JSON parsing for structured LLM outputs

⚠️ **Areas for Improvement**:
- Add type hints throughout (some functions lack them)
- Add docstrings to functions
- Handle edge cases (empty articles, API failures)
- Add unit tests
- Remove commented-out code

---

**Last Updated**: November 17, 2025
**Project Status**: 🟡 In Active Development (Core agents complete, integration pending)
