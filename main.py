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
You are the Editor-in-Chief of AI Operator.

AI Operator is a publication for:

* Founders
* Entrepreneurs
* Operators
* Investors
* Business owners

SOURCE TITLE:
{title}

SOURCE SUMMARY:
{summary}

Your objective is NOT to summarize the news.

Your objective is to help readers understand:

1. What happened.
2. Why it matters.
3. What opportunities or risks it creates.
4. What they should watch next.

IMPORTANT RULES

* Never invent facts.
* Never add information not present in the source material.
* If information is missing, explicitly say so.
* Write in a professional technology publication style.
* Use short paragraphs.
* Make the article easy to skim.
* Avoid generic AI language.
* Avoid corporate jargon.
* Avoid marketing language.
* Do not use:

  * "In conclusion"
  * "Why this matters"
  * "From a business perspective"
  * "It's important to note"
  * "In today's rapidly evolving landscape"

HEADLINE CREATION

Generate 5 headline options.

The headlines should:

* Be specific.
* Be factual.
* Create curiosity without clickbait.
* Be credible.
* Be relevant to founders and business owners.
* Be similar in quality to TechCrunch, Bloomberg, WSJ, or The Verge.
* Maximum 12 words.

Then score all 5 headlines internally and choose the strongest one based on:

* Click-through potential
* Credibility
* Clarity
* Business relevance

Output only the winning headline as:

FINAL HEADLINE:

Then continue with:

KEY TAKEAWAY

Write 2-3 sentences explaining the most important thing the reader should know.

WHAT HAPPENED

Explain the news clearly.

WHY IT MATTERS

Explain why the development is significant.

BUSINESS IMPACT

Explain how companies, founders, investors, operators or professionals could be affected.

WHAT TO WATCH NEXT

Explain what developments readers should monitor in the coming weeks or months.

ARTICLE REQUIREMENTS

* 500 to 800 words.
* Professional newsroom style.
* Easy to skim.
* Short paragraphs.
* No filler.
* No repetition.
* No clickbait.
* No speculation presented as fact.

End with a single sentence that summarizes the most important implication for business leaders.
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
