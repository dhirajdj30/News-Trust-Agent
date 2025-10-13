from db.check_last_update import latest_news_available



def is_updated():
    if not latest_news_available():
        print("⚠️ News articles table not updated in last 24h.")
        return False
    else:
        print("✅ News articles table is up-to-date.")
        return True