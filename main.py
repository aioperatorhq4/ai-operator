import os
import feedparser
from openai import OpenAI
from supabase import create_client

# -----------------------------
# CONFIG
# -----------------------------

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# AI SCORING SYSTEM
# -----------------------------

AI_KEYWORDS = {
    "ai": 3,
    "artificial intelligence": 3,
    "openai": 3,
    "chatgpt": 3,
    "anthropic": 3,
    "claude": 3,
    "gemini": 3,
    "deepmind": 3,
    "hugging face": 3,
    "llm": 3,
    "large language model": 3,
    "machine learning": 2,
    "neural network": 2,
    "transformer": 2,
    "generative ai": 2,
    "foundation model": 2,
    "gpu": 1,
    "inference": 1,
    "fine-tuning": 1,
    "prompt": 1,
    "rag": 1,
    "agent": 1,
    "agents": 1,
    "copilot": 1
}

NEGATIVE_KEYWORDS = [
    "football",
    "soccer",
    "baseball",
    "basketball",
    "tennis",
    "cricket",
    "weather",
    "election",
    "warship",
    "transfer",
    "premier league",
    "world cup",
    "championship",
    "goal",
    "match",
    "player",
    "coach"
]

# -----------------------------
# AI SCORE
# -----------------------------

def calculate_ai_score(text):
    text = text.lower()

    score = 0

    for keyword, points in AI_KEYWORDS.items():
        if keyword in text:
            score += points

    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text:
            score -= 3

    return score

# -----------------------------
# ARTICLE REWRITER
# -----------------------------

def rewrite_article(title, summary):

    prompt = f"""
You are a technology journalist.

Rewrite the following news into an original article.

TITLE:
{title}

SUMMARY:
{summary}

Requirements:
- 300 to 500 words
- Professional newspaper style
- Explain what happened
- Explain why it matters
- Explain possible business implications
- Do not copy the original wording
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# -----------------------------
# GET SOURCES
# -----------------------------

sources = supabase.table("sources").select("*").execute()

for source in sources.data:

    source_name = source["name"]
    source_url = source["url"]

    print(f"\nProcessing {source_name}")

    feed = feedparser.parse(source_url)

    for article in feed.entries[:20]:

        title = getattr(article, "title", "")
        summary = getattr(article, "summary", "")

        text_to_check = f"{title} {summary}"

        score = calculate_ai_score(text_to_check)

        print(f"Score {score}: {title}")

        if score < 3:
            continue

        slug = (
            title.lower()
            .replace(" ", "-")
            .replace("'", "")
            .replace('"', "")
        )

        existing = (
            supabase
            .table("articles")
            .select("id")
            .eq("slug", slug)
            .execute()
        )

        if existing.data:
            continue

        print("Rewriting article...")

        rewritten_article = rewrite_article(title, summary)

        data = {
            "title": title,
            "slug": slug,
            "summary": summary,
            "content": summary,
            "source": source_name,
            "category": "AI",
            "rewritten_article": rewritten_article
        }

        supabase.table("articles").insert(data).execute()

        print(f"Inserted: {title}")

print("\nFinished processing all sources")
