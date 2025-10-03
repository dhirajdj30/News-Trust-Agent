import psycopg2
from dotenv import load_dotenv
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


cur = conn.cursor()
# Example INSERTS
insert_queries = [
    # Insert into news_sources
    ("INSERT INTO news_sources (source_name, source_url) VALUES (%s, %s)", 
     ("Moneycontrol", "https://www.moneycontrol.com")),
    
    ("INSERT INTO news_sources (source_name, source_url) VALUES (%s, %s)", 
     ("CNBC", "https://www.cnbc.com")),

    # Insert into categories
    ("INSERT INTO categories (category_name) VALUES (%s)", 
     ("Finance",)),

    ("INSERT INTO categories (category_name) VALUES (%s)", 
     ("Sports",)),

    ("INSERT INTO categories (category_name) VALUES (%s)", 
     ("Seasonal",)),

    # Insert into news_ratings
    ("INSERT INTO news_ratings (source_id, category_id, rating) VALUES (%s, %s, %s)", 
     (1, 1, 7.5)),  # Moneycontrol, Finance
    
    ("INSERT INTO news_ratings (source_id, category_id, rating) VALUES (%s, %s, %s)", 
     (2, 2, 6.0)),  # CNBC, Sports

    # Insert into predictions
    ("INSERT INTO predictions (source_id, category_id, stock_symbol, target_date) VALUES (%s, %s, %s, %s)", 
     (1, 1, "TCS", "2025-10-05")),

    # Insert into feedback
    ("INSERT INTO feedback (prediction_id, user_id, outcome, rating) VALUES (%s, %s, %s, %s)", 
     (1, "user123", "Correct", 5)),

    # Insert into prediction_sources
    ("INSERT INTO prediction_sources (prediction_id, source_id, article_url, article_title, source_rating, llm_confidence, weight) VALUES (%s, %s, %s, %s, %s, %s, %s)",
     (1, 1, "https://moneycontrol.com/article", "TCS predicted to rise", 7.5, 0.85, 0.7)),

    # Insert into agent_logs
    ("INSERT INTO agent_logs (node_name, message) VALUES (%s, %s)",
     ("PredictionNode", '{"event": "prediction_created", "prediction_id": 1}'))
]

# Execute inserts
for query, data in insert_queries:
    cur.execute(query, data)

# Commit changes
conn.commit()

print("✅ Sample data inserted successfully!")

cur.close()
conn.close()