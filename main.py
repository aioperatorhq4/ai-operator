import os
import feedparser
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

sources = supabase.table("sources").select("*").execute()

for source in sources.data:
    feed = feedparser.parse(source["url"])

    for article in feed.entries[:5]:
        data = {
            "title": article.title,
            "slug": article.title.lower().replace(" ", "-"),
            "summary": getattr(article, "summary", ""),
            "content": getattr(article, "summary", ""),
            "source": source["name"],
            "category": "General"
        }

        supabase.table("articles").insert(data).execute()

print("Articles inserted successfully")
