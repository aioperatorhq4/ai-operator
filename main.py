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

Articles about major AI companies, AI models, AI products, AI research organizations, AI infrastructure providers, AI agents, AI developer tools, or AI-powered robotics should be included even if the terms "AI" or "artificial intelligence" are not explicitly used.

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

Before creating the headlines, ignore the wording of the source title.

Read the source content and identify the single most interesting element of the story.

This may be:

* A surprising fact
* A contradiction
* A business lesson
* A trend
* A problem being solved
* A change in behavior
* An opportunity
* A risk
* A strategic implication

Build the headline around that insight, not around the wording of the source title.

Evaluate all headline options using:

* Credibility
* Clarity
* Curiosity
* Business relevance
* Click-through potential

Select the strongest headline.

HEADLINE TYPE DETECTION

Before writing the headline, determine what type of content this is.

NEWS

Examples:

* Product launches
* Company announcements
* Funding rounds
* Acquisitions
* Partnerships
* Regulations
* Market developments

For news stories, focus on:

* Why it matters
* What changed
* The business implication
* The strategic lesson
* The surprising element

Preferred styles:

* Why...
* How...
* What ... Means
* The New Trend In...
* The Problem With...
* Inside...

GUIDES / RESEARCH / EDUCATIONAL CONTENT

Examples:

* Tutorials
* Technical guides
* Research explainers
* Frameworks
* Comparisons
* Engineering deep dives

For educational content, focus on:

* What the reader will learn
* The framework
* The concept
* The practical takeaway

Preferred styles:

* The X Types of...
* A Guide to...
* How X Works
* Understanding...
* The Framework Behind...
* Explained: ...

Do not force a news-style headline onto educational content.

Do not force an educational-style headline onto news content.

HEADLINE STRATEGY

Do not simply rewrite the source title.

The headline should be based on the story itself, not the source headline.

Identify the most interesting implication, lesson, trend, problem, opportunity, or surprising element in the story.

Prefer headlines that answer one of these questions:

* Why does this matter?
* What changed?
* What problem is being solved?
* What assumption is being challenged?
* What should founders, operators, or investors learn from this?

The headline should create curiosity while remaining completely truthful.

A reader who clicks the headline must find the promised information in the article.

The headline should be more compelling than the source title while remaining factually accurate.

Avoid generic product-announcement headlines.

Avoid headlines that merely describe what was announced.

Avoid press-release style headlines.

Prefer headlines that explain why the announcement is interesting.

Prefer headlines that reveal the significance of the story rather than the announcement itself.

When appropriate, use headline styles such as:

* Why...
* How...
* What ... Means
* The Case For...
* The New Trend In...
* The Problem With...
* Inside...
* The Shift Toward...

without forcing these formats.

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

* This publication covers Artificial Intelligence.
* The article must remain focused on AI, AI companies, AI products, AI research, AI regulation, AI adoption, AI investments, AI infrastructure, or AI business applications.
* If AI is not a central part of the story, do not force AI-related conclusions or implications.

SOURCE DEPTH RULES

* First assess how much information is available in the source material.

RICH SOURCE

A source is considered rich if it contains:

* Multiple facts
* Detailed explanations
* Quotes
* Data
* Product details
* Research findings
* Significant context

For rich sources, provide a more detailed article.

LIMITED SOURCE

A source is considered limited if it contains only:

* A headline
* A brief summary
* One or two facts
* Minimal context

For limited sources:

* Prioritize accuracy over completeness.
* Do not expand the story with assumptions.
* Do not invent analysis to reach a target length.
* Do not speculate about market impact, investor reactions, customer behavior, regulations, competition, adoption, or future developments unless explicitly supported by the source.
* Clearly state when information is limited.
* Keep the article concise.

A shorter accurate article is preferable to a longer speculative article.
If the source contains fewer than 100 words of information, do not infer business implications, investor implications, competitive implications, future developments, risks, opportunities, or market impact unless explicitly stated in the source.

It is acceptable to publish a 100–200 word article if that is all the source supports.

INSUFFICIENT INFORMATION RULE

If the source title and summary do not contain enough factual information to support a useful article, return exactly:

SKIP_ARTICLE

If the source material contains only an announcement, teaser, headline, brief description, or fewer than three concrete factual details, return exactly:

SKIP_ARTICLE

Do not attempt to fill gaps with assumptions.

Do not invent context.

Do not invent business implications.

Do not invent investor implications.

Do not invent competitive implications.

Do not invent risks, opportunities, or future developments.

A short source is acceptable only when it contains enough concrete facts to support an accurate article.

When in doubt, prefer SKIP_ARTICLE over speculation.

ARTICLE REQUIREMENTS

* Write only as much as the source material supports.
* Typical length: 250 to 700 words.
* Limited sources should produce shorter articles.
* Rich sources may produce longer articles.
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

    article = response.choices[0].message.content

    print("\nREWRITE RESPONSE:")
    print(article)
    print("\nEND RESPONSE\n")

    return article
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

        if not summary and hasattr(article, "content"):
            summary = article.content[0].value
        if len(summary.strip()) < 100:
           print("Skipped - insufficient source material (before GPT)")
           continue

        print("\nTITLE:")
        print(title)

        print("\nSUMMARY:")
        print(summary)

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
            print("Already processed. Skipping remaining articles from this source.")
            break

        print("Rewriting article...")

        try:
            rewritten_article = rewrite_article(title, summary)
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
            "content": summary,
            "source": source_name,
            "category": "AI",
            "rewritten_article": rewritten_article
        }

        supabase.table("articles").insert(data).execute()

        print(f"Inserted: {title}")

print("\nFinished processing all sources")
