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
# -----------------------------

# -----------------------------
# AI ARTICLE FILTER
# -----------------------------

def is_ai_article(title, summary):

    prompt = f"""
You are the editor of AI Operator.

Determine whether this article is primarily about Artificial Intelligence.

TITLE:
{title}

SUMMARY:
{summary}

INCLUDE articles primarily about:

* Artificial Intelligence
* Machine Learning
* Large Language Models
* OpenAI
* Anthropic
* Claude
* Gemini
* Google DeepMind
* AI startups
* AI products
* AI infrastructure
* AI chips
* AI research
* AI regulation
* AI investments
* AI adoption
* AI agents
* Robotics powered by AI

EXCLUDE articles primarily about:

* Politics
* Elections
* Wars
* Military conflict
* Crime
* Weather
* Sports
* Entertainment
* Celebrity news
* General business news
* Energy markets
* Geopolitics

even if AI is briefly mentioned.

Return only:

YES

or

NO
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

    answer = response.choices[0].message.content.strip().upper()

    return "YES" in answer

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

OUTPUT FORMAT RULES

The output must look like a published article.

Do NOT output:

* FINAL HEADLINE:
* HEADLINE:
* KEY TAKEAWAY
* WHAT HAPPENED
* WHY IT MATTERS
* BUSINESS IMPACT
* WHAT TO WATCH NEXT

Do NOT output any section labels.

The first line must be the headline.

Leave one blank line.

Then begin the article immediately.

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
# -----------------------------

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

        is_ai = is_ai_article(title, summary)

        print(f"AI Article: {is_ai} - {title}")

        if not is_ai:
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
