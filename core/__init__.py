from core.config import settings
from core.logger import setup_logger, logger
from core.db import supabase

# Expose these variables so they can be imported directly from the `core` module
__all__ = ["settings", "setup_logger", "logger", "supabase"]