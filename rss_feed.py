# import feedparser
# from bs4 import BeautifulSoup
# from datetime import datetime
# import schedule
# import time

# # Step 1: RSS feed URL
# RSS_STATIONS = {
#     "https://www.nseindia.com/rss-feed",
#     "https://in.investing.com/webmaster-tools/rss",
#     "https://www.business-standard.com/rss-feeds/listing",


# }
# RSS_FEED_URL = [
#     "https://www.moneycontrol.com/rss/latestnews.xml",
#     "https://www.livemint.com/rss/money",
#     "https://www.livemint.com/rss/markets",
#     "https://in.investing.com/rss/stock_Stocks.rss",
#     "https://in.investing.com/rss/stock_stock_picks.rss",
#     "https://in.investing.com/rss/news_25.rss",
#     "https://in.investing.com/rss/news_357.rss",
#     "https://nsearchives.nseindia.com/content/RSS/Annual_Reports.xml",
#     "https://nsearchives.nseindia.com/content/RSS/Daily_Buyback.xml",
#     "https://nsearchives.nseindia.com/content/RSS/Financial_Results.xml",
#     "https://nsearchives.nseindia.com/content/RSS/Insider_Trading.xml",
#     "https://www.business-standard.com/rss/markets-106.rss",

# ]

# # Step 2: Function to clean text
# def clean_text(html_text):
#     soup = BeautifulSoup(html_text, "html.parser")
#     return soup.get_text().strip()

# def ingest_moneycontrol_news():
#     # Parse RSS feed
#     print(f"Running ingestion at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     feed = feedparser.parse(RSS_FEED_URL[0])



#     for entry in feed.entries[:20]:  # Get last 20 articles
#         title = clean_text(entry.title)
#         link = entry.link
#         published = entry.get("published", datetime.now().isoformat())
#         summary = clean_text(entry.get("summary", ""))

#         print("Title: ", title)
#         print("link: ", link)
#         print("published: ", published)
#         print("summary: ", summary)



# # Step 5: Run
# if __name__ == "__main__":
#     ingest_moneycontrol_news()  # Run once at start
# schedule.every().minutes.do(ingest_moneycontrol_news)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
from db.insertion import insert_articles

# Step 1: RSS feed URLs
RSS_FEED_URLS = [
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://www.livemint.com/rss/money",
    "https://www.livemint.com/rss/markets",
    "https://in.investing.com/rss/stock_Stocks.rss",
    "https://in.investing.com/rss/stock_stock_picks.rss",
    "https://in.investing.com/rss/news_25.rss",
    "https://in.investing.com/rss/news_357.rss",
    # "https://nsearchives.nseindia.com/content/RSS/Annual_Reports.xml",
    # "https://nsearchives.nseindia.com/content/RSS/Daily_Buyback.xml",
    # "https://nsearchives.nseindia.com/content/RSS/Financial_Results.xml",
    # "https://nsearchives.nseindia.com/content/RSS/Insider_Trading.xml",
    "https://www.business-standard.com/rss/markets-106.rss",
]

RSS_FEED= {
    "moneycontrol" : ["https://www.moneycontrol.com/rss/latestnews.xml"],
    "livemint" : ["https://www.livemint.com/rss/money",
                    "https://www.livemint.com/rss/markets"],
    "investing":  ["https://in.investing.com/rss/stock_Stocks.rss",
                    "https://in.investing.com/rss/stock_stock_picks.rss",
                    "https://in.investing.com/rss/news_25.rss",
                    "https://in.investing.com/rss/news_357.rss"],
    # "https://nsearchives.nseindia.com/content/RSS/Annual_Reports.xml",
    # "https://nsearchives.nseindia.com/content/RSS/Daily_Buyback.xml",
    # "https://nsearchives.nseindia.com/content/RSS/Financial_Results.xml",
    # "https://nsearchives.nseindia.com/content/RSS/Insider_Trading.xml",
    "business-standard": ["https://www.business-standard.com/rss/markets-106.rss"],
}

CSV_FILE = "rssfeeds.csv"

# Step 2: Function to clean text
def clean_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text().strip()

# Step 3: Fetch and save all RSS feeds
def ingest_all_feeds():

    cnt = 0

    print(f"🔄 Running ingestion at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for source, urls in RSS_FEED.items():
        print(f"Source: {source}")
        for url in urls:
            print(f"  URL: {url}")
            print(f"📡 Fetching from: {url}")
            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:  # Limit to last 20 per feed
                source=source
                title=clean_text(entry.title)
                summary=clean_text(entry.get("summary", ""))
                link=entry.link
                published=entry.get("published", datetime.now().isoformat())

                article_id= insert_articles(source,url,title,link,published,summary)
                cnt += 1
                print(f"    ✅ Inserted article ID: {article_id} | Title: {title}")



    print(f"✅ Ingestion complete. Total articles inserted: {cnt}")


# Step 4: Run once
if __name__ == "__main__":
    ingest_all_feeds()
