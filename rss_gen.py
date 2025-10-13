from fastapi import FastAPI, Response
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin

app = FastAPI()

# Target URLs
URLS = [
    # "https://pulse.zerodha.com/",
    # "https://upstox.com/news/market-news/stocks/",
    "https://finance.yahoo.com/topic/stock-market-news/"

]

@app.get("/rss")
def rss():
    fg = FeedGenerator()
    fg.title("Market News RSS Feed")
    fg.link(href="https://pulse.zerodha.com/", rel="alternate")
    fg.description("Auto-generated RSS feed combining multiple market news sources.")
    fg.language("en")

    for url in URLS:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # 🎯 Custom extraction per website
        articles = []
        if "zerodha" in url:
            # Zerodha Pulse news cards
            articles = soup.select("article.post a")  # Only real articles
        elif "upstox" in url:
            # Upstox news page: filter only article links
            articles = soup.select("a[href*='/news/market-news/stocks/']")

        for a in articles:
            title = a.get_text(strip=True)
            link = a.get("href")

            if not title or not link:
                continue

            # Handle relative URLs
            link = urljoin(url, link)

            # Filter out unwanted links (like PDFs, disclosures, etc.)
            if not link.endswith(".pdf") and "risk-disclosures" not in link:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=link)

    # Limit to top 30 entries
    rss_feed = fg.rss_str(pretty=True)
    return Response(content=rss_feed, media_type="application/rss+xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
