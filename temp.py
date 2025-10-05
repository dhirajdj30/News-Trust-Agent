from sentence_transformers import SentenceTransformer
import psycopg2

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to PostgreSQL
conn = psycopg2.connect("dbname=news user=postgres password=secret")
cur = conn.cursor()

# Example article
title = "New AI breakthrough"
content = "Researchers developed a new AI model..."
embedding = model.encode(content).tolist()  # convert numpy array to list

# Insert article
cur.execute("""
    INSERT INTO news_articles (title, content, embedding)
    VALUES (%s, %s, %s)
""", (title, content, embedding))

conn.commit()
cur.close()
conn.close()
