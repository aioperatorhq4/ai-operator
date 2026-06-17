import os
import feedparser
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

rss_url = "http://feeds.bbci.co.uk/news/rss.xml"
feed = feedparser.parse(rss_url)

for article in feed.entries[:5]:
    data = {
        "title": article.title,
        "slug": article.title.lower().replace(" ", "-"),
        "summary": getattr(article, "summary", ""),
        "content": getattr(article, "summary", ""),
        "source": "BBC",
        "category": "World"
    }

    supabase.table("articles").insert(data).execute()

print("Articles inserted successfully")
