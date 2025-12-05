import hashlib
from datetime import datetime
from pathlib import Path
import json
import threading


class CrawlCache:
    """
    Thread-safe filesystem cache for crawled site data.
    """

    def __init__(self, cache_dir="./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.locks = {}
        self.lock = threading.Lock()

    def _get_url_lock(self, url):
        with self.lock:
            if url not in self.locks:
                self.locks[url] = threading.Lock()
            return self.locks[url]

    def _get_cache_key(self, url):
        return hashlib.sha256(url.encode()).hexdigest()

    def _get_cache_paths(self, url):
        """Return paths for metadata and text files for a URL."""
        key = self._get_cache_key(url)
        return {
            "metadata": self.cache_dir / f"{key}_metadata.json",
            "llms_txt": self.cache_dir / f"{key}_llms.txt",
            "llms_full_txt": self.cache_dir / f"{key}_llms_full.txt",
        }

    def _compute_structure_hash(self, pages):
        structure = sorted([
            (p.canonical_url, p.section, p.depth, p.is_optional)
            for p in pages
        ])
        return hashlib.sha256(str(structure).encode()).hexdigest()

    def _compute_content_hash(self, pages):
        content_hashes = sorted([p.content_hash for p in pages])
        return hashlib.sha256("".join(content_hashes).encode()).hexdigest()

    def get(self, url):
        """
        Return cached llms data and metadata for URL, or None on miss/error.
        """
        url_lock = self._get_url_lock(url)
        with url_lock:
            paths = self._get_cache_paths(url)
            if not all(p.exists() for p in paths.values()):
                return None

            try:
                metadata = json.loads(paths["metadata"].read_text())
            except Exception:
                return None

            try:
                return {
                    "llms_txt": paths["llms_txt"].read_text(),
                    "llms_full_txt": paths["llms_full_txt"].read_text(),
                    "metadata": metadata,
                    "from_cache": True
                }
            except Exception:
                return None

    def set(self, url, llms_txt, llms_full_txt, pages):
        """
        Persist llms artifacts and metadata for a URL.

        Computes structure/content hashes from pages for change detection.
        """
        url_lock = self._get_url_lock(url)
        with url_lock:
            paths = self._get_cache_paths(url)

            # use hashes for change detection
            structure_hash = self._compute_structure_hash(pages)
            content_hash = self._compute_content_hash(pages)
            metadata = {
                "url": url,
                "cached_at": datetime.now().isoformat(),
                "structure_hash": structure_hash,
                "content_hash": content_hash,
                "page_count": len(pages)
            }

            try:
                paths["metadata"].write_text(json.dumps(metadata, indent=2))
                paths["llms_txt"].write_text(llms_txt)
                paths["llms_full_txt"].write_text(llms_full_txt)
            except Exception as e:
                print(f"Error writing cache for {url}: {e}")

    def invalidate(self, url):
        """Delete all cached files for a URL."""
        url_lock = self._get_url_lock(url)
        with url_lock:
            paths = self._get_cache_paths(url)
            for path in paths.values():
                if path.exists():
                    path.unlink()

    def get_status(self, url):
        """
        Get cache status for a URL
        """
        paths = self._get_cache_paths(url)

        if not paths["metadata"].exists():
            return None

        try:
            metadata = json.loads(paths["metadata"].read_text())
            cached_time = datetime.fromisoformat(metadata["cached_at"])
            age = datetime.now() - cached_time

            return {
                "cached_at": metadata["cached_at"],
                "age_hours": age.total_seconds() / 3600,
                "page_count": metadata["page_count"]
            }
        except Exception:
            return None

    def clear_all_except(self, url):
        """
        Clear all cached files EXCEPT for the specified URL.
        Used to maintain only the most recently visited site.
        """
        keep_key = self._get_cache_key(url)

        for file_path in self.cache_dir.glob("*"):
            file_hash = file_path.stem.split("_")[0]

            # delete cache if it's not for the current URL
            if file_hash != keep_key:
                try:
                    file_path.unlink()
                    print(f"[Cache] Deleted old cache file: {file_path.name}")
                except Exception as e:
                    print(f"[Cache] Error deleting {file_path.name}: {e}")
