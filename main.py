import os
import feedparser
from supabase import create_client

# ----------------------------
# Supabase
# ----------------------------

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# AI Keywords
# ----------------------------

AI_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "openai",
    "chatgpt",
    "gpt",
    "anthropic",
    "claude",
    "gemini",
    "google ai",
    "llm",
    "large language model",
    "nvidia",
    "semiconductor",
    "chip",
    "robot",
    "robotics",
    "automation",
    "deep learning",
    "neural network"
]

# ----------------------------
# Helper
# ----------------------------

def is_ai_article(title, summary):
    text = f"{title} {summary}".lower()

    for keyword in AI_KEYWORDS:
        if keyword.lower() in text:
            return True

    return False

# ----------------------------
# Get RSS Sources
# ----------------------------

sources = supabase.table("sources").select("*").execute()

for source in sources.data:

    source_name = source["name"]
    rss_url = source["url"]

    print(f"Processing {source_name}")

    feed = feedparser.parse(rss_url)

    for article in feed.entries[:20]:

        title = article.get("title", "")
        summary = article.get("summary", "")

        if not is_ai_article(title, summary):
            continue

        slug = (
            title.lower()
            .replace(" ", "-")
            .replace("'", "")
            .replace('"', "")
            .replace(",", "")
            .replace(".", "")
        )

        # Check duplicate
        existing = (
            supabase
            .table("articles")
            .select("id")
            .eq("slug", slug)
            .execute()
        )

        if existing.data:
            continue

        data = {
            "title": title,
            "slug": slug,
            "summary": summary,
            "content": summary,
            "source": source_name,
            "category": "AI"
        }

        supabase.table("articles").insert(data).execute()

        print(f"Inserted: {title}")

print("Finished processing all sources")
