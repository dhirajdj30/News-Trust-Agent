-- Sources of news (Moneycontrol, CNBC, etc.)
CREATE TABLE news_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(255) UNIQUE NOT NULL,
    source_url TEXT
);

-- Categories (Finance, Sports, Seasonal, etc.)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

-- Ratings of sources per category
CREATE TABLE news_ratings (
    rating_id SERIAL PRIMARY KEY,
    source_id INT REFERENCES news_sources(source_id),
    category_id INT REFERENCES categories(category_id),
    rating FLOAT DEFAULT 5.0,  -- start neutral at 5/10
    rating_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_id, category_id)
);

-- Predictions made by your agent
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    source_id INT REFERENCES news_sources(source_id),
    category_id INT REFERENCES categories(category_id),
    stock_symbol VARCHAR(20) NOT NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_date DATE NOT NULL,
    outcome VARCHAR(20) DEFAULT 'Pending'  -- Pending, Correct, Wrong, Partial
);

-- Feedback from users after T+1 (or later)
CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    prediction_id INT REFERENCES predictions(prediction_id),
    user_id VARCHAR(50),
    outcome VARCHAR(20) CHECK (outcome IN ('Correct', 'Wrong', 'Partial')),
    rating INT CHECK (rating BETWEEN 1 AND 5), -- optional stars
    feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




-- Which sources influenced a prediction and with what weight
CREATE TABLE prediction_sources (
  id SERIAL PRIMARY KEY,
  prediction_id INT REFERENCES predictions(prediction_id),
  source_id INT REFERENCES news_sources(source_id),
  article_url TEXT,
  article_title TEXT,
  source_rating FLOAT,
  llm_confidence FLOAT,
  weight FLOAT
);

-- Agent logs for auditing
CREATE TABLE agent_logs (
  log_id SERIAL PRIMARY KEY,
  event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  node_name TEXT,
  message JSONB
);
