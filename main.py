import os
import feedparser
import trafilatura
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
* Autonomous systems driven by AI
* Enterprise AI applications
* AI developer tools
* AI model training and inference

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
* Transportation news that is not primarily about AI
* Startup news that is not primarily about AI
* Consumer technology news that is not primarily about AI
* General science news that is not primarily about AI

even if AI is briefly mentioned.

INCLUSION TEST

An article should be included if AI is the primary reason the story is newsworthy.

Articles about major AI companies, AI models, AI products, AI research organizations, AI infrastructure providers, AI agents, AI developer tools, 
or AI-powered robotics should be included even if the terms "AI" or "artificial intelligence" are not explicitly used.

Examples that should be INCLUDED:

* OpenAI
* ChatGPT
* GPT models
* Anthropic
* Claude
* Google DeepMind
* Gemini
* Perplexity
* Midjourney
* Cursor
* Windsurf
* Hugging Face
* NVIDIA AI platforms
* AI agents
* AI coding tools

Ask yourself:

"Is AI the primary reason this story exists?"

If YES, return YES.

If NO, return NO.

AI must be central to the story, not merely mentioned.
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

AI Operator is a publication for founders, entrepreneurs, operators, investors, and business owners.

SOURCE TITLE:
{title}

SOURCE ARTICLE:
{summary}

Your task is to rewrite the source into a publication-ready article.

OBJECTIVES

- Explain what happened.
- Explain why it matters.
- Explain the most relevant business, technical, or strategic implications supported by the source.
- Remain completely faithful to the source material.

FACTUALITY

- Never invent facts.
- Never add information that does not appear in the source.
- Never speculate.
- Never use outside knowledge.
- If important information is missing, say so instead of guessing.

HEADLINE

Create one compelling headline.

Do not simply rewrite the original title.

Read the entire article and identify the most interesting insight, trend, lesson, problem, opportunity, or implication.

The headline must:

- be truthful
- create curiosity
- accurately reflect the article
- avoid clickbait
- avoid press-release wording

OUTPUT

The first line must be the headline.

Leave one blank line.

Then immediately begin the article.

Do not include labels such as:

- HEADLINE
- KEY TAKEAWAY
- WHAT HAPPENED
- WHY IT MATTERS
- CONCLUSION

STYLE

- Professional technology publication.
- Short paragraphs.
- Easy to skim.
- Clear language.
- No marketing language.
- No corporate jargon.
- No repetition.
- No filler.

AI FOCUS

The publication covers Artificial Intelligence.

Keep the article focused on AI companies, products, research, infrastructure, regulation, investment, or business applications.

Do not force AI conclusions that are not supported by the source.

INSUFFICIENT INFORMATION

If the source does not contain enough factual information to produce a useful article, return exactly:

SKIP_ARTICLE

ARTICLE

Write only what the source supports.

Typical length:

250–700 words.

Shorter articles are acceptable when the available information is limited.
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

    article = response.choices[0].message.content

    print("\nREWRITE RESPONSE:")
    print(article)
    print("\nEND RESPONSE\n")

    return article


def get_article_text(url):

    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        return ""

    text = trafilatura.extract(downloaded)

    return text or ""
# -----------------------------
# -----------------------------

# -----------------------------

# GET SOURCES

# -----------------------------

AI_ONLY_SOURCES = [
    "OpenAI",
    "Anthropic",
    "Google DeepMind",
    "Hugging Face",
    "AI News",
    "MarkTechPost",
    "VentureBeat AI",
    "Ars Technica AI"
]

sources = supabase.table("sources").select("*").execute()

for source in sources.data:

    source_name = source["name"]
    source_url = source["url"]

    print(f"\nProcessing {source_name}")

    feed = feedparser.parse(source_url)

    for article in feed.entries[:20]:

        title = getattr(article, "title", "")
        summary = getattr(article, "summary", "")
        link = getattr(article, "link", "")

        # Download the full article
        full_text = get_article_text(link)

        # Fall back to RSS if extraction failed
        if not full_text:
            full_text = summary

        # If RSS has no summary, try RSS content
        if not full_text and hasattr(article, "content"):
            full_text = article.content[0].value

        # Skip articles with almost no content
        if len(full_text.strip()) < 100:
            print("Skipped - insufficient source material (before GPT)")
            continue

        print("\nTITLE:")
        print(title)

        print("\nLINK:")
        print(link)

        print("\nFULL ARTICLE:")
        print(full_text[:500])

        # Skip GPT classification for AI-only sources
        if source_name in AI_ONLY_SOURCES:
            is_ai = True
            print("AI Article: True (trusted AI source)")
        else:
            is_ai = is_ai_article(title, full_text)
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
            print("Already processed. Skipping remaining articles from this source.")
            break

        print("Rewriting article...")

        try:
            rewritten_article = rewrite_article(title, full_text)
        except Exception as e:
            print("OPENAI ERROR:", e)
            continue

        if rewritten_article.strip() == "SKIP_ARTICLE":
            print("Skipped - insufficient source material")
            continue

        data = {
            "title": title,
            "slug": slug,
            "summary": summary,
            "content": full_text,
            "source": source_name,
            "category": "AI",
            "rewritten_article": rewritten_article
        }

        supabase.table("articles").insert(data).execute()

        print(f"Inserted: {title}")

print("\nFinished processing all sources")
