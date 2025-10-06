from db.connection import get_connection
from psycopg2 import sql
import pandas as pd


def fetch_table(table_name):
    # Create a cursor
    conn = get_connection()
    cur = conn.cursor()
    # Use psycopg2.sql for safe table name interpolation
    query = sql.SQL("SELECT * FROM {table}").format(
        table=sql.Identifier(table_name)
    )

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    return rows

def fetch_todays_articles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT article_id, title, content, url, published_at
        FROM news_articles
        WHERE DATE(published_at) = CURRENT_DATE;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fetch_article_by_id(article_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT article_id, title, content, url, published_at
        FROM news_articles
        WHERE article_id = %s;
    """, (article_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def fetch_predictions():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT p.prediction_id, p.predicted_at, p.target_date,
               p.stocks_list, c.category_name, s.source_name, nr.rating
        FROM predictions p
        JOIN categories c ON p.category_id = c.category_id
        JOIN news_sources s ON p.source_id = s.source_id
        JOIN news_ratings nr ON s.source_id = nr.source_id AND c.category_id = nr.category_id
        ORDER BY p.predicted_at DESC LIMIT 20
    """, conn)
    conn.close()
    return df

def fetch_ratings():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT s.source_name, c.category_name, nr.rating, nr.rating_count
        FROM news_ratings nr
        JOIN news_sources s ON nr.source_id = s.source_id
        JOIN categories c ON nr.category_id = c.category_id
        ORDER BY s.source_name, c.category_name
    """, conn)
    conn.close()
    return df