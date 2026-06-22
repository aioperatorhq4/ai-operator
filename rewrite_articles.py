import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

articles = (
    supabase
    .table("articles")
    .select("id,title,created_at")
    .order("created_at", desc=True)
    .limit(50)
    .execute()
)

for article in articles.data:
    print(article["title"])
