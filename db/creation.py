import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
import os
load_dotenv()


dbname = os.getenv("dbname")
user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")


# Connection config
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)

# Create a cursor
cur = conn.cursor()

# Define schema creation queries
queries = [
    """
    CREATE TABLE IF NOT EXISTS news_sources (
        source_id SERIAL PRIMARY KEY,
        source_name VARCHAR(255) UNIQUE NOT NULL,
        source_url TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR(100) UNIQUE NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS news_ratings (
        rating_id SERIAL PRIMARY KEY,
        source_id INT REFERENCES news_sources(source_id),
        category_id INT REFERENCES categories(category_id),
        rating FLOAT DEFAULT 5.0,
        rating_count INT DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (source_id, category_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS predictions (
        prediction_id SERIAL PRIMARY KEY,
        source_id INT REFERENCES news_sources(source_id),
        category_id INT REFERENCES categories(category_id),
        stock_symbol VARCHAR(20) NOT NULL,
        predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        target_date DATE NOT NULL,
        outcome VARCHAR(20) DEFAULT 'Pending'
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id SERIAL PRIMARY KEY,
        prediction_id INT REFERENCES predictions(prediction_id),
        user_id VARCHAR(50),
        outcome VARCHAR(20) CHECK (outcome IN ('Correct', 'Wrong', 'Partial')),
        rating INT CHECK (rating BETWEEN 1 AND 5),
        feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS prediction_sources (
        id SERIAL PRIMARY KEY,
        prediction_id INT REFERENCES predictions(prediction_id),
        source_id INT REFERENCES news_sources(source_id),
        article_url TEXT,
        article_title TEXT,
        source_rating FLOAT,
        llm_confidence FLOAT,
        weight FLOAT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_logs (
        log_id SERIAL PRIMARY KEY,
        event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        node_name TEXT,
        message JSONB
    );
    """
]

# Execute each query
for q in queries:
    cur.execute(q)

# Commit changes
conn.commit()

print("✅ Tables created successfully!")

# Close cursor and connection
cur.close()
conn.close()
