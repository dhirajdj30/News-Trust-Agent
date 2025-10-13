from db.connection import get_connection


def save_category(article_id, category_name, confidence):
    # Create a cursor
    conn = get_connection()
    cur = conn.cursor()

    # Ensure category exists
    cur.execute("SELECT category_id FROM categories WHERE category_name = %s", (category_name,))
    row = cur.fetchone()
    if row:
        category_id = row[0]
    else:
        cur.execute("INSERT INTO categories (category_name) VALUES (%s) RETURNING category_id;", (category_name,))
        category_id = cur.fetchone()[0]

    print(row)
    print(category_id)
    print(category_name)
    print(confidence)

    # Update article with classification
    cur.execute("""
        UPDATE news_articles
        SET category_id = %s, llm_confidence = %s
        WHERE article_id = %s
    """, (category_id, confidence, article_id))

    conn.commit()
    cur.close()
    conn.close()



def insert_articles(source,url,title,link,published,summary):
    conn = get_connection()
    cur = conn.cursor()

    # Ensure dummy source exists"

    cur.execute("INSERT INTO news_sources (source_name, source_url) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
        (source, url))
    conn.commit()
    cur.execute("SELECT article_id FROM news_articles WHERE url = %s;", (link,))
    existing = cur.fetchone()
    if existing:
        print(f"⚠️ Duplicate found, skipping: {title}")
        cur.close()
        conn.close()
        return None  # No new insert
    cur.execute("""
        INSERT INTO news_articles (source_id, title, content, url, published_at)
        VALUES (
            (SELECT source_id FROM news_sources WHERE source_name=%s),
            %s, %s, %s, %s
        ) RETURNING article_id;
    """, (
        source,
        title,
        summary,
        link,
        published
    ))

    article_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()
    return article_id


def all_insertion():
    # Create a cursor
    conn = get_connection()
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

if __name__ == "__main__":
    all_insertion()
