from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import hashlib
from .crawler import crawl_site
from .generator import generate_llms_txt, generate_llms_full_txt
from .cache import CrawlCache

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = CrawlCache(cache_dir="./cache")

class CrawlRequest(BaseModel):
    """Request body for crawl-related endpoints."""
    url: str

@app.post("/api/crawl")
def crawl(req: CrawlRequest):
    """
    Crawl a site and return llms.txt and llms-full.txt.

    Uses a time-based (30 min) and hash-based cache:
    - Returns recent cache if available.
    - Otherwise re-crawls, detects changes via structure/content hashes,
      regenerates outputs if needed, and updates the cache.
    """
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        # try to get data from cache first and check for changes
        cached_data = cache.get(url)
        if cached_data:
            cached_time = datetime.fromisoformat(cached_data["metadata"]["cached_at"])
            age = datetime.now() - cached_time
            if age.total_seconds() < 1800:
                return {
                    "llms_txt": cached_data["llms_txt"],
                    "llms_full_txt": cached_data["llms_full_txt"],
                    "from_cache": True,
                    "cached_at": cached_data["metadata"]["cached_at"]
                }

            result = crawl_site(url)
            pages = result.pages
            structure = sorted([
                (p.canonical_url, p.section, p.depth, p.is_optional)
                for p in pages
            ])

            new_structure_hash = hashlib.sha256(str(structure).encode()).hexdigest()
            content_hashes = sorted([p.content_hash for p in pages])
            new_content_hash = hashlib.sha256("".join(content_hashes).encode()).hexdigest()
            old_structure_hash = cached_data["metadata"]["structure_hash"]
            old_content_hash = cached_data["metadata"]["content_hash"]

            if new_structure_hash == old_structure_hash and new_content_hash == old_content_hash:
                cache.set(url, cached_data["llms_txt"], cached_data["llms_full_txt"], pages)
                return {
                    "llms_txt": cached_data["llms_txt"],
                    "llms_full_txt": cached_data["llms_full_txt"],
                    "from_cache": True,
                    "cached_at": cached_data["metadata"]["cached_at"],
                    "checked_at": datetime.now().isoformat()
                }

            llms_txt = generate_llms_txt(pages)
            llms_full_txt = generate_llms_full_txt(pages)
            cache.set(url, llms_txt, llms_full_txt, pages)

            return {
                "llms_txt": llms_txt,
                "llms_full_txt": llms_full_txt,
                "from_cache": False,
                "cached_at": datetime.now().isoformat(),
                "change_detected": True
            }

        result = crawl_site(url)
        pages = result.pages
        llms_txt = generate_llms_txt(pages)
        llms_full_txt = generate_llms_full_txt(pages)
        cache.set(url, llms_txt, llms_full_txt, pages)

        return {
            "llms_txt": llms_txt,
            "llms_full_txt": llms_full_txt,
            "from_cache": False,
            "cached_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cache/status")
def get_cache_status(url: str):
    """
    Return cache status and metadata for a URL.

    If a cache entry exists, returns `cached=True` plus stored metadata;
    otherwise returns `cached=False`.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    status = cache.get_status(url)
    if not status:
        return {"cached": False, "url": url}

    return {"cached": True, "url": url, **status}


@app.post("/api/cache/invalidate")
def invalidate_cache(req: CrawlRequest):
    """
    Invalidate any cached crawl result for the given URL.

    Deletes the cache entry so the next crawl forces a fresh fetch.
    """
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    cache.invalidate(url)
    return {"message": f"Cache invalidated for {url}"}