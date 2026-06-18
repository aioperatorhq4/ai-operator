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
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "large language model",
    "llm",
    "chatgpt",
    "openai",
    "gpt-4",
    "gpt-5",
    "claude",
    "anthropic",
    "gemini",
    "copilot",
    "midjourney",
    "stability ai",
    "hugging face",
    "generative ai",
    "ai model",
    "ai startup",
    "ai company",
    "ai tool",
    "ai assistant"
]
# ----------------------------
# Helper
# ----------------------------

def is_ai_article(title, summary):
    text = f"{title} {summary}".lower()

    for keyword in AI_KEYWORDS:
        if keyword in text:
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
