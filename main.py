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

Return ONLY:

TRUE

or

FALSE

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

    return answer == "TRUE"

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

Evaluate whether the source contains enough factual information to support a standalone news article.

Return exactly:

SKIP_ARTICLE

if ANY of the following are true:

* The source contains fewer than three concrete factual details.
* The source is primarily an announcement, teaser, press release, promotional content, or event notice.
* The source is mainly opinion or commentary rather than reporting.
* The source lacks sufficient context to accurately explain the story.
* The source discusses multiple unrelated stories, such as a newsletter, daily roundup, or weekly digest.
* The source does not focus on a single primary news event.

Do not explain your decision.

SECOND STEP

Identify the single central news event.

Ignore the wording of the original headline.

Ask yourself:

"What is the most important news in this article?"

If there is no single dominant story, return:

SKIP_ARTICLE

Create a new headline that captures the significance of the story rather than simply describing the announcement.

The headline should be truthful, specific, and driven by the article's central insight.

Avoid headlines that simply state:

* Company X launches...
* Company Y announces...

Instead, when appropriate, prefer headline styles such as:

* Why...
* How...
* Inside...
* What ... Means
* The Shift Toward...
* The Problem With...

Never exaggerate.

Never promise information the article does not contain.

The headline must accurately reflect the article the reader is about to read.

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
# CATEGORY CLASSIFIER
# -----------------------------

def classify_category(title, article):

    prompt = f"""
You are the Editor of AI Operator.

Classify this article into EXACTLY ONE category.

TITLE:
{title}

ARTICLE:
{article}

Choose ONE of the following categories:

- AI Models
- AI Companies
- AI Startups
- AI Research
- AI Infrastructure
- AI Chips
- AI Agents
- AI Robotics
- AI Regulation
- AI Investments
- Enterprise AI
- AI Developer Tools

Guidelines:

AI Models
- New foundation models, LLMs, multimodal models, releases, benchmarks.

AI Companies
- Major AI companies, acquisitions, partnerships, executive changes.

AI Startups
- Startup launches, funding, growth, products.

AI Research
- Papers, benchmarks, scientific discoveries, academic research.

AI Infrastructure
- Datacenters, cloud AI, compute, inference, training infrastructure.

AI Chips
- GPUs, NPUs, AI accelerators, semiconductors.

AI Agents
- Autonomous agents, copilots, agent frameworks.

AI Robotics
- Physical robots powered by AI.

AI Regulation
- Government policy, legislation, legal decisions, compliance.

AI Investments
- Funding rounds, venture capital, investments, acquisitions.

Enterprise AI
- AI adoption by businesses, enterprise software, productivity.

AI Developer Tools
- SDKs, APIs, coding assistants, developer platforms.

Return ONLY the category name.

Do not explain.
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

    return response.choices[0].message.content.strip()

# -----------------------------

# GET SOURCES

# -----------------------------


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

       is_ai = is_ai_article(title, full_text)
       print(f"AI Article: {is_ai} - {title}")

       if not is_ai:
           continue

      category = classify_category(title, full_text)
      print(f"Category: {category}")

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
         "category": category,
         "rewritten_article": rewritten_article
}
        supabase.table("articles").insert(data).execute()

        print(f"Inserted: {title}")

print("\nFinished processing all sources")
