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

Generate 5 headline options internally.

Evaluate them using:

* Credibility
* Clarity
* Curiosity
* Business relevance
* Click-through potential

Select the strongest headline.

Display ONLY the selected headline.

Do NOT display:

* Alternative headlines
* Scores
* Reasoning
* "Winning headline"
* "Final headline"
* Any labels or explanations

The first line of the output must be the headline itself.

The second line must begin the article.

CRITICAL FACTUALITY RULES

* Use only information explicitly present in the source title and source summary.
* Never add facts from your own knowledge.
* Never add statistics unless they appear in the source.
* Never add dates, locations, people, companies, products, or events unless they appear in the source.
* Never assume context that is not provided.
* If information is limited, clearly say so.
* If a conclusion cannot be supported by the source, do not make it.
* Accuracy is more important than completeness.

AI RELEVANCE RULE

This publication covers Artificial Intelligence.

The article must remain focused on AI, AI companies, AI products, AI research, AI regulation, AI adoption, AI investments, AI infrastructure, or AI business applications.

If AI is not a central part of the story, do not force AI-related conclusions or implications.

ARTICLE REQUIREMENTS

* Write 400 to 700 words.
* Professional newsroom style.
* Easy to skim.
* Short paragraphs.
* No filler.
* No repetition.
* No clickbait.
* No speculation presented as fact.
* Explain what happened.
* Explain why it may be relevant.
* Explain potential implications only when supported by the source.

The output should read like a published article ready to appear on AI Operator.
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
