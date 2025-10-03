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