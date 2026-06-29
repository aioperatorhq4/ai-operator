import os
import feedparser
import trafilatura

from concurrent.futures import ThreadPoolExecutor

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

AI Operator covers artificial intelligence for founders, operators, investors and business leaders.

You are writing a published news article, not a summary.

Your first responsibility is factual accuracy.

Use ONLY the information contained in the source article.

If a fact is not explicitly stated, do not write it.

Never use outside knowledge.

Never speculate.

Never predict.

Never infer business impact unless the source explicitly supports it.

If information is missing, simply don't mention it.

--------------------------------------------------

INPUT

TITLE

{title}

ARTICLE

{summary}

--------------------------------------------------

FIRST STEP

Determine whether the source contains enough factual information.

Return exactly:

SKIP_ARTICLE

if ANY of these are true:

• fewer than three concrete facts
• mostly an announcement
• teaser article
• promotional article
• press release
• event announcement
• article shorter than about 150 words
• mostly opinions
• insufficient context

Do not explain.

--------------------------------------------------

SECOND STEP

Identify the central news.

Ignore the wording of the original headline.

Ask yourself:

What is actually interesting here?

Build a new headline around that.

The headline should explain significance.

Never write:

Company X launches...

Company Y announces...

Instead prefer:

Why...

How...

Inside...

What ... Means

The Shift Toward...

The Problem With...

only when appropriate.

Never exaggerate.

Never promise something the article doesn't deliver.

--------------------------------------------------

THIRD STEP

Write the article.

Length:

250–500 words.

Only exceed 500 words if the source is exceptionally detailed.

Write like:

The Information

Financial Times

Reuters

Bloomberg

NOT like ChatGPT.

NOT like a blog.

NOT like LinkedIn.

Use:

Short paragraphs.

Direct language.

No filler.

No repetition.

--------------------------------------------------

STYLE RULES

Never write:

"In conclusion"

"Why this matters"

"From a business perspective"

"It is important to note"

"In today's rapidly evolving landscape"

"Overall"

"Ultimately"

"This highlights"

"This underscores"

"This signals"

"This demonstrates"

Instead, simply present the facts.

Let the reader draw conclusions.

--------------------------------------------------

STRICT FACTUAL RULES

Never add:

market implications

competitive implications

future implications

investor implications

business opportunities

strategic lessons

unless explicitly discussed in the source.

Never explain something using your own knowledge.

Never define companies.

Never define technologies.

Never provide historical context unless present.

--------------------------------------------------

HEADLINE

Output ONLY one headline.

No labels.

--------------------------------------------------

OUTPUT FORMAT

Headline

(blank line)

Article

--------------------------------------------------

Remember:

Accuracy is more important than completeness.

A shorter factual article is always better than a longer speculative one.
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

    for article in feed.entries[:5]:

        title = getattr(article, "title", "")
        summary = getattr(article, "summary", "")
        link = getattr(article, "link", "")

        slug = (
            title.lower()
            .replace(" ", "-")
            .replace("'", "")
            .replace('"', "")
        )

        # Check if already processed BEFORE downloading the article
        existing = (
            supabase
            .table("articles")
            .select("id")
            .eq("slug", slug)
            .execute()
        )

        if existing.data:
            print("Already processed.")
            continue

        # Download the full article
        full_text = get_article_text(link)

        # Fall back to RSS summary
        if not full_text:
            full_text = summary

        # Fall back to RSS content
        if not full_text and hasattr(article, "content"):
            full_text = article.content[0].value

        # Skip tiny articles
        if len(full_text.strip()) < 100:
            print("Skipped - insufficient source material (before GPT)")
            continue

        print("\nTITLE:")
        print(title)

        print("\nLINK:")
        print(link)

        print("\nFULL ARTICLE:")
        print(full_text[:500])

        # Skip GPT classification for trusted AI sources
        if source_name in AI_ONLY_SOURCES:
            is_ai = True
            print("AI Article: True (trusted AI source)")
        else:
            is_ai = is_ai_article(title, full_text)
            print(f"AI Article: {is_ai} - {title}")

        if not is_ai:
            continue

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
