from db.connection import get_connection
from psycopg2 import sql



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
