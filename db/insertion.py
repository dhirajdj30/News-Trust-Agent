from db.connection import get_connection
import csv




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



def insert_articles_from_csv(csv_path):
    conn = get_connection()
    cur = conn.cursor()

    # Ensure dummy source exists
    cur.execute("INSERT INTO news_sources (source_name, source_url) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                ("CSV Feed", "local_csv"))
    conn.commit()

    article_ids = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute("""
                INSERT INTO news_articles (source_id, title, content, url, published_at)
                VALUES (
                    (SELECT source_id FROM news_sources WHERE source_name=%s),
                    %s, %s, %s, %s
                ) RETURNING article_id;
            """, (
                row["source"],
                row["title"],
                row["summary"],
                row["link"],
                row["published"]
            ))

            article_id = cur.fetchone()[0]
            article_ids.append(article_id)

    conn.commit()
    cur.close()
    conn.close()
    return article_ids


def insert_dummy_article():
    # Create a cursor
    conn = get_connection()
    cur = conn.cursor()

    # Ensure dummy source exists
    cur.execute("INSERT INTO news_sources (source_name, source_url) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                ("Moneycontrol", "https://www.moneycontrol.com/rss/latestnews.xml"))
    conn.commit()

    # Insert dummy article
    cur.execute("""
        INSERT INTO news_articles (source_id, title, content, url)
        VALUES (
            (SELECT source_id FROM news_sources WHERE source_name=%s),
            %s, %s, %s
        ) RETURNING article_id;
    """, (
        "Moneycontrol",
        "Heavy rains expected to boost umbrella sales in Mumbai",
        "Analysts suggest seasonal demand will drive short-term stock gains for umbrella companies.",
        "https://dummynews.com/umbrella-sales"
    ))

    article_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Dummy article inserted with ID {article_id}")
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

