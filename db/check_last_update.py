from db.connection import get_connection
from datetime import datetime, timedelta, timezone

def latest_news_available():
    conn = get_connection()
    cur = conn.cursor()

    table_name = "news_articles"

    # Fetch last vacuum and analyze times
    cur.execute("""
        SELECT
            GREATEST(
                COALESCE(last_vacuum, 'epoch'::timestamp),
                COALESCE(last_autovacuum, 'epoch'::timestamp),
                COALESCE(last_analyze, 'epoch'::timestamp),
                COALESCE(last_autoanalyze, 'epoch'::timestamp)
            ) AS last_activity
        FROM pg_stat_all_tables
        WHERE relname = %s;
    """, (table_name,))

    result = cur.fetchone()
    last_activity = result[0] if result else None

    # Handle no activity
    if not last_activity or last_activity == datetime(1970, 1, 1):
        print("❌ Table has no recorded activity!")
        return False

    time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)

    conn.close()
    if last_activity > time_threshold:
        print(f"✅ Table '{table_name}' was active within 24 hours — skipping insert.")
        return True
    else:
        print(f"⚠️ Table '{table_name}' inactive for >24h — running insert.")
        return False


# Run check
if __name__== "__main__":
    latest_news_available()