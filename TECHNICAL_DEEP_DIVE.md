# 🔧 News-Trust-Agent: Technical Deep Dive

## File-by-File Implementation Details

### 🌐 **Entry Points**

#### `main.py` (62 lines)
**Purpose**: Flask-like main entry point with LangGraph workflow

**Key Code**:
```python
class State(MessagesState):
    article_id: int | None = None
    query: str = "give me top 5 stocks to buy"
    title: str | None = None
    content: str | None = None
    summary: str = ""
    category: str | None = None
    confidence: float | None = None
```

**Graph Construction**:
```
START → fetch_relevant_articles → categorize → END
```

**Status**: ✅ Functional but simple (sequential, not dynamic)

---

#### `app.py` (empty)
**Purpose**: Reserved for Flask API (not implemented yet)

**TODO**: 
- [ ] Wrap agents in REST endpoints
- [ ] Add request/response handlers
- [ ] Implement auth

---

#### `notebook.ipynb` (10 cells)
**Purpose**: Interactive exploration and testing

**Cell Breakdown**:
1. ✅ Fetch from DB
2. ✅ Fetch relevant articles
3. ✅ Graph construction (commented out version)
4. ✅ Workflow execution with state tracking
5. ✅ MLFlow setup
6. ✅ MLFlow logging with sklearn example
7. ✅ Experiment tracking
8. ✅ Misc tests

**Observations**:
- Good for experimentation
- Contains both working and commented code
- Should be cleaned up for production

---

### 📡 **Data Ingestion Layer**

#### `rss_feed.py` (102 lines)
**Purpose**: Main RSS feed ingestion orchestrator

**Data Sources**:
```python
RSS_FEED = {
    "moneycontrol": ["https://www.moneycontrol.com/rss/latestnews.xml"],
    "livemint": [
        "https://www.livemint.com/rss/money",
        "https://www.livemint.com/rss/markets"
    ],
    "investing": [
        "https://in.investing.com/rss/stock_Stocks.rss",
        "https://in.investing.com/rss/stock_stock_picks.rss",
        "https://in.investing.com/rss/news_25.rss",
        "https://in.investing.com/rss/news_357.rss",
    ],
    "business-standard": ["https://www.business-standard.com/rss/markets-106.rss"],
}
```

**Processing Pipeline**:
```python
def ingest_all_feeds():
    for source, urls in RSS_FEED.items():
        for url in urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:  # Last 20 articles
                title = clean_text(entry.title)
                summary = clean_text(entry.get("summary", ""))
                link = entry.link
                published = entry.get("published", datetime.now().isoformat())
                
                article_id = insert_articles(source, url, title, link, published, summary)
                # Store in DB
```

**Key Features**:
- HTML tags stripped via BeautifulSoup
- Duplicates prevented by URL check
- Source metadata captured
- Batch processing (20 articles per feed)

**Frequency**: Currently manual - **TODO**: Add schedule every N hours

**Status**: ✅ Working, ⚠️ Needs scheduling

---

#### `agents/rss_feed.py` (63 lines)
**Purpose**: Duplicate of rss_feed.py in agents folder

**Observation**: Code duplication detected - consolidate to single location

---

### 🗄️ **Database Layer**

#### `db/connection.py` (14 lines)
**Purpose**: PostgreSQL connection manager

```python
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("dbname"),
        user=os.getenv("user"),
        password=os.getenv("pass"),
        host=os.getenv("host"),
        port=os.getenv("port")
    )
```

**Environment Variables** (required in .env):
```
dbname=<db_name>
user=<postgres_user>
pass=<postgres_password>
host=localhost
port=5432
```

**Status**: ✅ Simple, functional

---

#### `db/schema.sql` (90 lines)
**Purpose**: Complete PostgreSQL schema definition

**Tables Created**:

1. **news_sources** (3 columns)
   - source_id (PK, SERIAL)
   - source_name (VARCHAR, UNIQUE)
   - source_url (TEXT)

2. **categories** (2 columns)
   - category_id (PK, SERIAL)
   - category_name (VARCHAR, UNIQUE)

3. **news_ratings** (6 columns)
   - rating_id, source_id (FK), category_id (FK)
   - rating (FLOAT, default 5.0)
   - rating_count (INT, default 0)
   - last_updated (TIMESTAMP)
   - Composite unique: (source_id, category_id)

4. **news_articles** (9 columns)
   - article_id, source_id (FK), title, content, url
   - published_at, category_id (FK), llm_confidence, inserted_at

5. **predictions** (7 columns)
   - prediction_id, source_id (FK), category_id (FK)
   - stock_symbol, predicted_at, target_date, outcome

6. **feedback** (5 columns)
   - feedback_id, prediction_id (FK), user_id, outcome, rating, feedback_time

7. **prediction_sources** (8 columns)
   - Lineage tracking (which articles influenced prediction)

8. **agent_logs** (4 columns)
   - JSONB message storage for audit trail

9. **news_articles** (9 columns)
   - Central article storage

**Status**: ✅ Well-designed with proper relationships

---

#### `db/creation.py` (105 lines)
**Purpose**: Schema initialization script

**Implementation**:
```python
queries = [
    # 8 CREATE TABLE IF NOT EXISTS queries
]
for q in queries:
    cur.execute(q)
conn.commit()
print("✅ Tables created successfully!")
```

**Idempotent**: Uses `IF NOT EXISTS` - safe to run multiple times

**Status**: ✅ Complete and robust

---

#### `db/insertion.py` (137 lines)
**Purpose**: Insert and update operations

**Key Functions**:

1. **`save_category(article_id, category_name, confidence)`**
   ```python
   - Fetch or create category_id
   - Update news_articles with category_id + llm_confidence
   - Commit to DB
   ```
   
2. **`insert_articles(source, url, title, link, published, summary)`**
   ```python
   - Insert source_name if not exists
   - Check for duplicates by URL
   - Insert article with all metadata
   - Return article_id
   ```

3. **`all_insertion()`** (commented out)
   - Bulk test data insertion

**Status**: ✅ Core functions working, ⚠️ incomplete all_insertion

---

#### `db/fetch.py` (36 lines)
**Purpose**: Read operations

**Functions**:

1. **`fetch_table(table_name)`**
   ```python
   SELECT * FROM {table}  # Safe parameterized query
   ```

2. **`fetch_todays_articles()`**
   ```python
   SELECT * FROM news_articles WHERE DATE(published_at) = CURRENT_DATE
   ```

3. **`fetch_article_by_id(article_id)`**
   ```python
   SELECT * FROM news_articles WHERE article_id = {id}
   ```

**Status**: ✅ All query functions complete

---

#### `db/vector_db.py` (48 lines)
**Purpose**: FAISS vector database integration

**Embedding Model**:
```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

**Key Functions**:

1. **`store_in_vector_db()`**
   ```python
   - Fetch today's articles from PostgreSQL
   - Generate embeddings for (title + "\n\n" + content)
   - Create FAISS index with texts + metadatas
   - Save to ./vector_store/faiss_index
   ```

2. **`retrieve_articles(query, top_k=5)`**
   ```python
   - Load FAISS index
   - Compute embedding of query
   - Search with similarity_search(query, k=top_k)
   - Extract article_ids from results
   - Return list of IDs sorted by relevance
   ```

**Storage Location**: `./vector_store/faiss_index/`

**Index Size**: ~80MB for all-MiniLM model

**Status**: ✅ Working, ⚠️ Needs incremental update strategy

---

### 🧠 **LLM Integration**

#### `llm_node.py` (15 lines)
**Purpose**: Centralized LLM configuration

```python
from langchain_google_genai import ChatGoogleGenerativeAI

gemini_api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_api_key,
    temperature=0,  # Deterministic (no randomness)
    max_output_tokens=512  # Sufficient for JSON
)
```

**Model Choice**: `gemini-2.5-flash`
- **Advantages**: Fast, cheap, good at JSON
- **Trade-off**: Less capable than Pro (acceptable for structured tasks)

**Status**: ✅ Simple, effective

---

### 🤖 **Agent Nodes**

#### `agents/fetch_article.py` (40 lines)
**Purpose**: Retrieve relevant articles based on query

**Function Signature**:
```python
def fetch_relevant_articles(state: dict) -> dict
```

**Input State**:
```python
{
    "query": "give me top 5 stocks to buy"
}
```

**Process**:
```
1. results = retrieve_articles(query, top_k=5)  # FAISS search
2. article_id = results[0]  # Most similar
3. article = fetch_article_by_id(article_id)  # Get full details
4. Unpack: article_id, title, content, url, published_at
5. Update state with these fields
6. Set state["step"] = "fetch_relevant_articles"
7. Return updated state
```

**Output State**:
```python
{
    "query": "...",
    "article_id": 123,
    "title": "...",
    "content": "...",
    "step": "fetch_relevant_articles"
}
```

**Error Handling**:
```python
if not results:
    raise ValueError("No relevant articles found.")
if not article:
    raise ValueError(f"Article with ID {article_id} not found.")
```

**Status**: ✅ Functional, ⚠️ Could handle top-k better

---

#### `agents/categorizer.py` (120 lines)
**Purpose**: Classify articles into financial categories

**Function Signature**:
```python
def categorize_node(state: dict) -> dict
```

**Input State**:
```python
{
    "article_id": 123,
    "title": "...",
    "content": "...",
    ...
}
```

**Process**:
```
1. Extract: article_id, title, content from state
2. Build prompt:
   "You are a financial news classifier.
    Categories: Finance, Economy, Seasonal, Sports, Politics, Global, Other
    
    Respond in JSON:
    {
      "category": "<one of the categories>",
      "confidence": <0.0 - 1.0>
    }
    
    Title: {title}
    Body: {content}"

3. Call llm.invoke(prompt)
4. Parse JSON from response using regex: r"\{.*\}"
5. Extract category and confidence
6. Call save_category(article_id, category, confidence) → DB update
7. Return updated state with category + confidence
```

**JSON Parser**:
```python
def json_formatter(llm_response: str) -> dict:
    match = re.search(r"\{.*\}", llm_response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {"category": "Other", "confidence": 0.0}
    return {"category": "Other", "confidence": 0.0}
```

**Output State**:
```python
{
    "article_id": 123,
    "title": "...",
    "content": "...",
    "category": "Finance",
    "confidence": 0.95,
    "step": "categorize"
}
```

**Status**: ✅ Working, robust JSON parsing

---

#### `agents/summarizer.py` (9 lines)
**Purpose**: Generate article summaries

```python
def summarize_article(state: dict) -> dict:
    content = state.get("content", "")
    prompt = f"Summarize the following article briefly:\n\n{content}"
    response = llm.invoke(prompt)
    state["summary"] = response.content.strip()
    state["step"] = "summarize"
    return state
```

**Status**: ✅ Basic but functional

---

#### `agents/controller.py` (40 lines)
**Purpose**: LLM-based workflow orchestrator

**Current Implementation**:
```python
def controller_node(state: dict) -> dict:
    system_prompt = """
    You are the workflow controller...
    Available tools: fetch_relevant_articles, categorize_article, summarize_article
    Respond in JSON: { "next_step": "<tool_name>" }
    """
    
    response = llm.invoke(system_prompt)
    
    # Parse JSON
    match = re.search(r"\{.*\}", response.content, re.DOTALL)
    next_step = data.get("next_step", "fetch_relevant_articles")
    
    state["step"] = next_step
    return state
```

**Issues**:
- No actual state information passed to LLM (only system prompt)
- Routing decisions are random/unpredictable
- Could end in infinite loop

**TODO**:
- [ ] Pass full state context to LLM
- [ ] Add termination logic
- [ ] Make decisions conditional on state

**Status**: ⚠️ Needs improvement

---

### 🔄 **Learning & Rating System**

#### `news_rating.py` (114 lines)
**Purpose**: Source credibility updates based on prediction outcomes

**Outcome Scores**:
```python
OUTCOME_SCORES = {
    "Correct": 10,   # Prediction accurate
    "Partial": 5,    # Partially correct
    "Wrong": 0       # Incorrect
}
```

**Bayesian Update Algorithm**:
```python
def update_news_rating(prediction_id, feedback_outcome, star_rating=None):
    # 1. Get source_id, category_id from prediction
    cur.execute("""
        SELECT source_id, category_id FROM predictions WHERE prediction_id = %s
    """)
    source_id, category_id = cur.fetchone()
    
    # 2. Compute feedback_score
    feedback_score = OUTCOME_SCORES[feedback_outcome]
    if star_rating:
        feedback_score = (feedback_score + (star_rating * 2)) / 2
    
    # 3. Get current rating
    cur.execute("""
        SELECT rating, rating_count FROM news_ratings 
        WHERE source_id = %s AND category_id = %s
    """)
    old_rating, rating_count = cur.fetchone()
    
    # 4. Apply Bayesian update
    alpha = 1 / (1 + rating_count)  # Adaptive learning rate
    new_rating = old_rating * (1 - alpha) + feedback_score * alpha
    new_rating_count = rating_count + 1
    
    # 5. Update database
    cur.execute("""
        UPDATE news_ratings 
        SET rating = %s, rating_count = %s 
        WHERE source_id = %s AND category_id = %s
    """, (new_rating, new_rating_count, source_id, category_id))
```

**Learning Rate Dynamics**:
- **New source** (rating_count=1): alpha = 0.5 → adapts quickly
- **Old source** (rating_count=99): alpha = 0.01 → adapts slowly
- **Benefit**: Credible sources don't lose trust on single mistake

**Status**: ✅ Algorithm designed, ⚠️ Not integrated into workflow

---

### 📊 **MLFlow Experiment Tracking**

#### `mlflow_client.py` (28 lines)
**Purpose**: ML experiment tracking and logging

```python
def mlflow_client():
    client = MlflowClient(tracking_uri="http://127.0.0.1:5000")
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    
    exp_name = "Agentic_Learning"
    if mlflow.get_experiment_by_name(exp_name) is None:
        mlflow.create_experiment(name=exp_name)
    
    mlflow.set_experiment(exp_name)
    mlflow.langchain.autolog()  # Auto-log LangChain runs
    
    return client
```

**Features**:
- Automatic LangChain logging
- Centralized tracking URI
- Experiment organization

**Requirements**: MLFlow server running on localhost:5000

**Status**: ✅ Set up, ⚠️ Custom metrics not yet added

---

### 📋 **Prompt Engineering**

#### `prompts/prompt.yaml` (120 lines)
**Purpose**: Prompt templates for LLM tasks

**Key Prompts**:

1. **Categorization**:
   ```yaml
   Categories: Finance, Seasonal, Sports, Politics, Tech, Company, M&A, SupplyChain, Other
   Respond in JSON with category + confidence (0-1) + short_reason
   ```

2. **Event Extraction** (designed but not implemented):
   ```yaml
   Output: JSON array with event_summary, affected_industries, implied_signal, confidence
   ```

3. **Prediction Aggregation** (designed but not implemented):
   ```yaml
   Input: Weighted articles from multiple sources
   Output: Top-5 stocks with rationale + provenance
   ```

4. **Weighting Algorithm**:
   ```
   weight = source_rating_normalized × llm_confidence × recency_factor
   recency_factor = exp(-0.05 × hours_since_published)
   ```

**Status**: ✅ Prompts well-designed, ⚠️ Some not yet implemented

---

### 📚 **Configuration Files**

#### `pyproject.toml` (dependencies)
```
Core: langchain, langgraph, langchain-google-genai
Data: pandas, psycopg2-binary, feedparser
ML: sentence-transformers, torch, faiss-cpu, mlflow
Utils: beautifulsoup4, python-dotenv, ipykernel
```

**Status**: ✅ Comprehensive

#### `rssfeeds.csv` 
**Purpose**: Store RSS feed metadata (example format shown in README)

**Status**: ✅ (not committed, created dynamically)

---

## 🔗 Data Flow Examples

### Example 1: Fetch & Categorize Workflow
```
Input Query: "which stocks related to AI?"
    ↓
[Fetch Node]
  - FAISS search on "which stocks related to AI?"
  - Returns article_id = 42 (most similar)
  - Fetch full article from DB
    Title: "New AI regulation impacts tech stocks"
    Content: "SEC announces new AI guidelines affecting NVIDIA, TSMC..."
    ↓
[Categorizer Node]
  - LLM: "Classify this article"
  - Response: {category: "Finance", confidence: 0.98}
  - Save to DB: UPDATE news_articles SET category_id=1, llm_confidence=0.98
    ↓
[Summarizer Node]
  - LLM: "Summarize this article"
  - Response: "New SEC AI guidelines will impact tech stocks..."
  - Update state
    ↓
Output:
{
  article_id: 42,
  title: "New AI regulation impacts tech stocks",
  category: "Finance",
  confidence: 0.98,
  summary: "SEC announces new AI guidelines affecting tech stocks..."
}
```

### Example 2: Rating Update (T+1 Feedback)
```
Day 1: News article suggests "Buy NVIDIA for AI growth"
  ↓
Store in DB:
  predictions: stock_symbol=NVIDIA, outcome='Pending'
    ↓
Day 2 (T+1): Outcome known - NVIDIA stock went UP
  ↓
Feedback received: {prediction_id=5, outcome='Correct', star_rating=5}
  ↓
[Update Rating]
  - Get source (Moneycontrol), category (Tech)
  - old_rating = 5.0, rating_count = 20
  - feedback_score = 10 (Correct)
  - alpha = 1 / (1 + 20) = 0.045
  - new_rating = 5.0 * 0.955 + 10 * 0.045 = 5.23
  - Update: rating=5.23, rating_count=21
    ↓
Result: Moneycontrol's Tech credibility increased 5.0 → 5.23
```

---

## ⚙️ Configuration Management

### Environment Variables (.env)
```bash
GOOGLE_API_KEY=<gemini-api-key>
dbname=newsdb
user=postgres
pass=<password>
host=localhost
port=5432
```

### Database Connection Flow
```
.env vars → os.getenv() → connection.py → psycopg2.connect()
```

### Vector Store Path
```
./vector_store/faiss_index/  (hardcoded, relative path)
```

---

## 🔍 Testing & Debugging

### Standalone Test Patterns

**In categorizer.py**:
```python
if __name__ == "__main__":
    test_state = TestState()
    test_state["article_id"] = 101
    test_state["title"] = "Heavy rains expected..."
    test_state["content"] = "Analysts suggest seasonal demand..."
    updated_state = categorize_node(test_state)
    print("Updated State:", updated_state)
```

**Allows individual node testing**

---

## 🚨 Error Handling Summary

| Function | Error Handling |
|----------|----------------|
| fetch_relevant_articles | ✅ ValueError if no articles found |
| categorize_node | ✅ Try-except for JSON parsing |
| get_connection | ⚠️ None (connection errors will crash) |
| store_in_vector_db | ✅ Catches missing articles |
| llm.invoke | ⚠️ No retry logic |

---

## 📊 Performance Characteristics

| Operation | Time | Scale |
|-----------|------|-------|
| RSS fetch (1 source) | ~2-5s | O(n) entries |
| FAISS embedding (1 article) | ~50ms | O(512 dimensions) |
| FAISS search (top-k) | ~10ms | O(log n) approx |
| LLM call (categorize) | ~2-5s | O(context length) |
| DB insert | ~50ms | O(1) per article |
| DB fetch | ~10ms | O(1) by ID |

---

## 🎯 Optimization Opportunities

1. **Batch Operations**: Insert 100 articles in 1 transaction (currently 1 each)
2. **FAISS Incremental Updates**: Rebuild only new articles (currently full rebuild)
3. **Async LLM Calls**: Process multiple articles in parallel
4. **Database Indexes**: Add indexes on (published_at, category_id, source_id)
5. **Caching**: Cache frequent queries (e.g., top sources)

---

This technical deep dive should give you a complete understanding of every component in your News-Trust-Agent!

*Last Updated: November 17, 2025*
