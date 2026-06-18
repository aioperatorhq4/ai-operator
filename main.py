import os
import feedparser
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

sources = supabase.table("sources").select("*").execute()

for source in sources.data:
    print(f"Processing {source['name']}")

    feed = feedparser.parse(source["url"])

    for article in feed.entries[:5]:

        article_url = getattr(article, "link", "")

        existing = (
            supabase
            .table("articles")
            .select("id")
            .eq("slug", article_url)
            .execute()
        )

        if existing.data:
            print(f"Skipping duplicate: {article.title}")
            continue

        data = {
            "title": article.title,
            "slug": article_url,
            "summary": getattr(article, "summary", ""),
            "content": getattr(article, "summary", ""),
            "source": source["name"],
            "category": "General"
        }

        supabase.table("articles").insert(data).execute()

        print(f"Inserted: {article.title}")

print("Finished processing all sources")
