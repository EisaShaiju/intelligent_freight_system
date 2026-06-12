# core/db.py
from supabase import create_client, Client
from core.config import settings

# Initialize a single client connection instance to Supabase
if not settings.supabase_url or not settings.supabase_key:
    raise ValueError(" Missing SUPABASE_URL or SUPABASE_KEY environment variables in .env file.")

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)