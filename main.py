import feedparser

rss_url = "http://feeds.bbci.co.uk/news/rss.xml"

feed = feedparser.parse(rss_url)

print("Latest Articles:")

for article in feed.entries[:5]:
    print(article.title)
