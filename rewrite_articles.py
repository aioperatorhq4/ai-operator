import os
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

articles = (
    supabase
    .table("articles")
    .select("*")
    .order("created_at", desc=True)
    .limit(1)
    .execute()
)

article = articles.data[0]

print("\nARTICLE DATA:\n")
print(article)
