
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from db.insertion import insert_articles

RSS_FEED= {
    "moneycontrol" : ["https://www.moneycontrol.com/rss/latestnews.xml"],
    "livemint" : ["https://www.livemint.com/rss/money",
                    "https://www.livemint.com/rss/markets"],
    "investing":  ["https://in.investing.com/rss/stock_Stocks.rss",
                    "https://in.investing.com/rss/stock_stock_picks.rss",
                    "https://in.investing.com/rss/news_25.rss",
                    "https://in.investing.com/rss/news_357.rss"],
    # "nseindia":  ["https://nsearchives.nseindia.com/content/RSS/Annual_Reports.xml",
    #                 "https://nsearchives.nseindia.com/content/RSS/Daily_Buyback.xml",
    #                 "https://nsearchives.nseindia.com/content/RSS/Financial_Results.xml",
    #                 "https://nsearchives.nseindia.com/content/RSS/Insider_Trading.xml"],
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
                if article_id:
                    cnt += 1
                print(f"    ✅ Inserted article ID: {article_id} | Title: {title}")



    print(f"✅ Ingestion complete. Total articles inserted: {cnt}")


# Step 4: Run once
if __name__ == "__main__":
    ingest_all_feeds()
