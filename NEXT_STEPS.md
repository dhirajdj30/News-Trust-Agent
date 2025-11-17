# 🎯 Next Steps & Implementation Roadmap

## Quick Status Check

✅ **COMPLETED (Production Ready)**
- RSS feed ingestion from 6 financial sources
- PostgreSQL schema with 9 properly-designed tables
- Semantic search with FAISS vector database
- LLM integration (Gemini 2.5 Flash)
- Article categorization (9 categories)
- Agentic workflow with LangGraph
- MLFlow experiment tracking
- Source rating algorithm (Bayesian)

⚠️ **IN PROGRESS (Needs Completion)**
- T+1 feedback loop (not scheduled)
- Stock prediction aggregation (missing)
- Dynamic controller routing (basic)
- Event extraction (not implemented)

---

## 🚀 Priority 1: Complete the News Agent (This Week)

### Task 1.1: Implement Stock Prediction Node
**Goal**: Generate top-5 stock recommendations by aggregating and weighting articles

**Difficulty**: Medium | **Time**: 4-6 hours

**Steps**:

1. **Create `agents/predictor.py`**:
```python
from llm_node import llm
from db.fetch import fetch_article_by_id
import json, re

def prediction_node(state):
    """
    Input: Categorized articles from previous nodes
    Output: Top-5 stock recommendations with rationales
    
    Process:
    1. Retrieve recent categorized articles from DB
    2. Calculate weight for each article:
       weight = (source_rating/10) × llm_confidence × recency_factor
    3. Group by implied stock symbols
    4. For top-5 by weight, prompt LLM for recommendations
    5. Save to predictions table
    """
    
    # Get top articles from DB
    articles = fetch_weighted_articles(state, limit=20)
    
    if not articles:
        state["error"] = "No articles to make predictions"
        return state
    
    # Prepare context for LLM
    context = format_articles_for_prediction(articles)
    
    prompt = f"""
    You are a financial advisor analyzing recent news.
    Based on these weighted articles, recommend the top 5 stocks to BUY.
    
    Articles (with credibility weights):
    {context}
    
    Respond in JSON:
    {{
      "predictions": [
        {{
          "symbol": "AAPL",
          "rationale": "Strong AI demand expected...",
          "confidence": 0.85,
          "target_date": "2025-11-24"
        }},
        ...
      ],
      "reasoning": "Overall market outlook..."
    }}
    """
    
    response = llm.invoke(prompt)
    result = parse_json_response(response.content)
    
    # Save predictions to DB
    for pred in result.get("predictions", []):
        save_prediction(state, pred, articles)
    
    state["predictions"] = result
    state["step"] = "predict"
    return state

def fetch_weighted_articles(state, limit=20):
    """Fetch recent articles with weights"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT na.article_id, na.title, na.content, 
               nr.rating, na.llm_confidence, na.published_at
        FROM news_articles na
        LEFT JOIN news_sources ns ON na.source_id = ns.source_id
        LEFT JOIN news_ratings nr ON ns.source_id = nr.source_id
        WHERE na.category_id IS NOT NULL
        ORDER BY na.published_at DESC
        LIMIT %s
    """, (limit,))
    
    articles = []
    for row in cur.fetchall():
        article_id, title, content, source_rating, confidence, pub_at = row
        
        # Calculate weight
        source_norm = (source_rating or 5.0) / 10.0
        conf = confidence or 0.5
        hours_ago = (datetime.now() - pub_at).total_seconds() / 3600
        recency = math.exp(-0.05 * hours_ago)
        
        weight = source_norm * conf * recency
        articles.append({
            "article_id": article_id,
            "title": title,
            "content": content,
            "weight": weight
        })
    
    cur.close()
    conn.close()
    
    # Sort by weight
    articles.sort(key=lambda x: x["weight"], reverse=True)
    return articles

def save_prediction(state, prediction, source_articles):
    """Save prediction to DB with lineage"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Insert prediction
    cur.execute("""
        INSERT INTO predictions (source_id, category_id, stock_symbol, target_date, outcome)
        VALUES (
            (SELECT source_id FROM news_sources LIMIT 1),
            (SELECT category_id FROM categories WHERE category_name='Finance' LIMIT 1),
            %s, %s, 'Pending'
        )
        RETURNING prediction_id
    """, (prediction["symbol"], prediction.get("target_date", "2025-11-24")))
    
    prediction_id = cur.fetchone()[0]
    
    # Link source articles (prediction lineage)
    for article in source_articles[:5]:  # Top 5 articles
        cur.execute("""
            INSERT INTO prediction_sources 
            (prediction_id, source_id, article_url, article_title, weight)
            VALUES (%s, (SELECT source_id FROM news_sources LIMIT 1), '', %s, %s)
        """, (prediction_id, article["title"], article["weight"]))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return prediction_id
```

2. **Update `main.py` to include prediction node**:
```python
graph.add_node("predict_stocks", prediction_node)
graph.add_edge("categorize", "predict_stocks")
graph.add_edge("predict_stocks", "END")
```

3. **Test with sample query**:
```bash
python main.py
```

**Acceptance Criteria**:
- ✅ Node accepts state from categorizer
- ✅ Generates JSON with top-5 stocks
- ✅ Saves to predictions table
- ✅ Includes lineage tracking

---

### Task 1.2: Implement T+1 Feedback Scheduler
**Goal**: Automatically update source ratings 1 day after predictions

**Difficulty**: Medium | **Time**: 3-4 hours

**Steps**:

1. **Create `agents/feedback_processor.py`**:
```python
import schedule
import time
from datetime import datetime, timedelta
from db.connection import get_connection
from news_rating import update_news_rating

def process_t_plus_1_feedback():
    """
    Run daily to:
    1. Find predictions made 1 day ago
    2. Check stock performance
    3. Update source ratings
    """
    print(f"🔄 Processing T+1 feedback at {datetime.now()}")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Get predictions from exactly 1 day ago
    one_day_ago = datetime.now() - timedelta(days=1)
    
    cur.execute("""
        SELECT prediction_id, stock_symbol, outcome
        FROM predictions
        WHERE outcome = 'Pending'
        AND predicted_at >= %s - INTERVAL '1 day'
        AND predicted_at < %s
    """, (one_day_ago, datetime.now()))
    
    predictions = cur.fetchall()
    
    for prediction_id, symbol, _ in predictions:
        # Determine outcome (simplified: assume 50% correct)
        # TODO: Integrate with real stock price API
        feedback_outcome = evaluate_prediction(symbol)  # "Correct", "Wrong", "Partial"
        
        # Update rating
        update_news_rating(prediction_id, feedback_outcome, star_rating=None)
        
        # Update prediction outcome
        cur.execute("""
            UPDATE predictions 
            SET outcome = %s 
            WHERE prediction_id = %s
        """, (feedback_outcome, prediction_id))
        
        print(f"  ✅ Updated prediction {prediction_id}: {feedback_outcome}")
    
    conn.commit()
    cur.close()
    conn.close()

def evaluate_prediction(symbol):
    """
    Fetch stock price from API and determine if prediction was correct
    
    TODO: Integrate with stock price API (yfinance, polygon.io, etc.)
    """
    # Placeholder
    return "Correct"  # Random for now

def schedule_feedback():
    """Schedule T+1 feedback to run daily at 9 AM"""
    schedule.every().day.at("09:00").do(process_t_plus_1_feedback)
    
    print("📅 T+1 Feedback scheduler started (runs daily at 09:00)")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_feedback()
```

2. **Add to main workflow** (alternative entry point):
```bash
# Start feedback processor in background
python -m agents.feedback_processor &
```

3. **Test with manual trigger**:
```python
# In notebook:
from agents.feedback_processor import process_t_plus_1_feedback
process_t_plus_1_feedback()  # Run manually
```

**Acceptance Criteria**:
- ✅ Finds predictions from 1 day ago
- ✅ Calls `update_news_rating()` correctly
- ✅ Updates prediction outcomes
- ✅ Scheduler runs daily

---

### Task 1.3: Improve Controller Node
**Goal**: Make controller decisions deterministic and state-aware

**Difficulty**: Easy | **Time**: 1-2 hours

**Changes to `agents/controller.py`**:

```python
def controller_node(state):
    """
    Improved controller with state-aware routing
    """
    
    # Decision logic based on current state
    if state.get("step") == "fetch_relevant_articles":
        # After fetch, always categorize
        next_step = "categorize_article"
    
    elif state.get("step") == "categorize_article":
        # After categorize, decide based on article type
        category = state.get("category", "Other")
        if category == "Finance":
            next_step = "predict_stocks"
        else:
            next_step = "summarize_article"
    
    elif state.get("step") == "predict_stocks":
        # After prediction, end workflow
        next_step = END
    
    elif state.get("step") == "summarize_article":
        # After summary, end workflow
        next_step = END
    
    else:
        # First call - start with fetch
        next_step = "fetch_relevant_articles"
    
    print(f"🧭 Controller routing to: {next_step}")
    state["step"] = next_step
    return state
```

**Acceptance Criteria**:
- ✅ Deterministic routing (not random)
- ✅ Considers current state
- ✅ Proper workflow sequence

---

## 📊 Priority 2: Testing & Validation (Next Week)

### Task 2.1: Write Unit Tests
```bash
# Create tests/test_agents.py
pytest tests/ -v
```

```python
import pytest
from agents.categorizer import categorize_node, json_formatter

def test_categorizer_valid_response():
    """Test categorizer with valid JSON response"""
    state = {
        "article_id": 1,
        "title": "Stock market surge",
        "content": "Markets went up today..."
    }
    result = categorize_node(state)
    assert "category" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1

def test_json_formatter():
    """Test JSON parsing"""
    response = '{"category": "Finance", "confidence": 0.95}'
    result = json_formatter(response)
    assert result["category"] == "Finance"
    assert result["confidence"] == 0.95

def test_json_formatter_with_garbage():
    """Test fallback on invalid JSON"""
    response = "This is not JSON"
    result = json_formatter(response)
    assert result["category"] == "Other"
    assert result["confidence"] == 0.0
```

### Task 2.2: End-to-End Testing
```python
# In notebook
from main import graph

# Test full workflow
test_state = State(query="Should I buy Apple stock?")
result = graph.invoke(test_state)

# Verify all steps completed
assert result.get("article_id") is not None
assert result.get("category") is not None
assert result.get("confidence") is not None
assert result.get("predictions") is not None  # After implementing predictor

print("✅ End-to-end workflow successful!")
```

### Task 2.3: Load Testing
```python
# Test with 100 articles
import time
from db.vector_db import store_in_vector_db

start = time.time()
store_in_vector_db()
end = time.time()

print(f"⏱️ Vector DB storage: {end - start:.2f}s")
```

---

## 🔗 Priority 3: Integration with USI System (Weeks 2-3)

### Task 3.1: Define API Contract
```python
# news_agent_api.py
from typing import TypedDict

class NewsSignal(TypedDict):
    stock_symbol: str
    signal: str  # "BUY", "HOLD", "SELL"
    confidence: float  # 0-1
    rationale: str
    source_articles: list[str]  # URLs

def get_news_signals() -> list[NewsSignal]:
    """Called by USI coordinator"""
    # Run workflow
    # Return signals
    pass
```

### Task 3.2: Build Data Bridge to Technical Agent
```python
# Connect news signals to technical analysis
# Combine signals for better predictions
```

### Task 3.3: Build Data Bridge to Fundamental Agent
```python
# Combine all three agents into unified system
# Generate final Buy/Hold/Sell recommendation
```

---

## 📋 Implementation Checklist

### Week 1 (THIS WEEK)
- [ ] Task 1.1: Implement prediction node (4-6 hours)
- [ ] Task 1.2: Implement T+1 feedback scheduler (3-4 hours)
- [ ] Task 1.3: Improve controller routing (1-2 hours)
- [ ] Task 2.1: Write unit tests (2-3 hours)
- [ ] **Total**: ~14-18 hours

### Week 2
- [ ] Task 2.2: End-to-end testing
- [ ] Task 2.3: Load testing & optimization
- [ ] Fix bugs from testing
- [ ] Documentation cleanup

### Week 3+
- [ ] Task 3.1-3.3: Integration with USI system
- [ ] Deployment & monitoring

---

## 🛠️ Code Quality Improvements

### Before Implementation
```bash
# Fix existing issues
1. Remove commented-out code (or save to archive)
2. Add type hints to all functions
3. Add docstrings
4. Consolidate RSS feed code (rss_feed.py vs agents/rss_feed.py)
```

### Example:
```python
# Before
def fetch_relevant_articles(state):
    query = state.get("query", "")

# After
from typing import TypedDict

class ArticleState(TypedDict):
    query: str
    article_id: int | None
    title: str | None
    content: str | None

def fetch_relevant_articles(state: ArticleState) -> ArticleState:
    """
    Retrieve the most relevant article from vector DB.
    
    Args:
        state: Article processing state
        
    Returns:
        Updated state with article_id, title, content
        
    Raises:
        ValueError: If no relevant articles found
    """
    query: str = state.get("query", "")
    # ...
```

---

## 🚨 Critical Bugs to Fix

1. **Empty `app.py`**: Needs Flask endpoint implementation
2. **Duplicate RSS ingestion code**: Consolidate rss_feed.py and agents/rss_feed.py
3. **No error retry logic**: LLM API calls might fail
4. **FAISS rebuild every time**: Should be incremental
5. **No API timeouts**: Long-running requests could hang

---

## 📚 Reference Implementation Timeline

```
Week 1: CORE (Stock prediction + T+1)
├─ Mon-Tue: Predictor node
├─ Tue-Wed: T+1 feedback scheduler
├─ Wed: Controller improvements
└─ Thu-Fri: Testing

Week 2: VALIDATION
├─ Mon-Tue: Unit tests & integration tests
├─ Wed-Thu: Load testing & optimization
└─ Fri: Bug fixes

Week 3: INTEGRATION
├─ Mon: API contract definition
├─ Tue-Thu: Integration with other agents
└─ Fri: End-to-end testing
```

---

## 🎁 Quick Wins (1-2 hours each)

If you want quick improvements while working on larger tasks:

1. **Add database indexes** (5 mins)
   ```sql
   CREATE INDEX idx_articles_published ON news_articles(published_at);
   CREATE INDEX idx_articles_category ON news_articles(category_id);
   CREATE INDEX idx_ratings_source_cat ON news_ratings(source_id, category_id);
   ```

2. **Add logging to stderr** (15 mins)
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   logger.info("Processing article...")
   ```

3. **Add README for running locally** (30 mins)
   ```bash
   # Installation
   uv sync
   
   # Setup
   python db/creation.py
   python -m rss_feed  # Ingest articles
   python -c "from db.vector_db import store_in_vector_db; store_in_vector_db()"
   
   # Run
   jupyter notebook
   ```

4. **Clean up notebook cells** (30 mins)
   - Remove all commented code
   - Add markdown section headers
   - Keep only essential test cells

---

## 💡 Success Criteria for Completion

### News Agent Complete When:
- ✅ RSS feeds continuously ingesting articles
- ✅ Articles automatically categorized (99%+ categories assigned)
- ✅ Predictions generated daily (top-5 stocks)
- ✅ T+1 feedback loop updating source ratings
- ✅ Source ratings correlate with prediction accuracy
- ✅ End-to-end workflow runs in < 30 seconds
- ✅ No errors in MLFlow experiment tracking

### Ready for USI Integration When:
- ✅ News signals (BUY/HOLD/SELL) exported to API
- ✅ Confidence scores calibrated
- ✅ Lineage tracking working (which articles influenced which predictions)
- ✅ Can be called from external system
- ✅ Documented API contract

---

## 📞 Support Resources

### Debugging LLM Responses
```python
# Log raw LLM response
print(f"Raw response: {response.content}")
```

### Database Debugging
```python
# Run manual queries
psql newsdb -U postgres
SELECT * FROM predictions ORDER BY predicted_at DESC LIMIT 5;
```

### MLFlow Debugging
```bash
# View experiments
mlflow ui --port 5000
```

---

**Next Action**: Start with Task 1.1 (Prediction Node) - this is foundational for everything else!

*Estimated Total Time to Completion*: 3-4 weeks (working ~10-15 hours/week)

*Last Updated: November 17, 2025*
