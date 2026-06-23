import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

articles = (
    supabase
    .table("articles")
    .select("id,title,summary")
    .order("created_at", desc=True)
    .limit(50)
    .execute()
)

article = articles.data[0]

print("\nTITLE:")
print(article["title"])

print("\nSUMMARY:")
print(article["summary"])
