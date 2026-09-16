import hashlib
import json
from pathlib import Path

CACHE_FILE = Path(".ragshield_cache.json")

def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}

def save_cache(cache):
    CACHE_FILE.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def cache_key(text: str):
    return hashlib.md5(text.encode("utf-8")).hexdigest()
