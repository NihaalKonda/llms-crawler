import threading
import time
from datetime import datetime
import hashlib
from .crawler import crawl_site
from .generator import generate_llms_txt, generate_llms_full_txt
from .cache import CrawlCache

class SiteMonitor:
    """
    Background monitor that continuously checks the currently viewed site for changes.

    When user views a new site, the old one is automatically replaced.
    Checks every 30 minutes for changes.
    """

    def __init__(self, cache: CrawlCache, check_interval=1800):
        self.cache = cache
        self.check_interval = check_interval
        self.current_url = None
        self.last_checked = None
        self.version = 1
        self.lock = threading.Lock()
        self.running = False
        self.monitor_thread = None

    def start(self):
        """Start the background monitoring thread"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """Stop the background monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def set_active_site(self, url):
        """
        Set the currently monitored site.
        Replaces any previously monitored site.
        """
        with self.lock:
            if url != self.current_url:
                self.current_url = url
                self.last_checked = datetime.now()
                self.version = 1

    def get_current_site(self):
        """Get the currently monitored site"""
        with self.lock:
            return self.current_url

    def get_version(self, url):
        """Get current version number for the active URL"""
        with self.lock:
            if url == self.current_url:
                return self.version
        return 0

    def _monitor_loop(self):
        """Background loop that checks the active site periodically"""
        while self.running:
            try:
                self._check_current_site()
            except Exception as e:
                print(f"[Monitor] Error in monitor loop: {e}")

            for _ in range(30):
                if not self.running:
                    break
                time.sleep(1)

    def _check_current_site(self):
        """Check the currently active site for changes"""
        with self.lock:
            url = self.current_url
            last_check = self.last_checked
        if not url or not last_check:
            return

        age = (datetime.now() - last_check).total_seconds()
        if age < self.check_interval:
            return
        cached_data = self.cache.get(url)
        if not cached_data:
            with self.lock:
                self.last_checked = datetime.now()
            return

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

        #update last checked timestamp
        with self.lock:
            self.last_checked = datetime.now()
        if new_structure_hash == old_structure_hash and new_content_hash == old_content_hash:
            self.cache.set(url, cached_data["llms_txt"], cached_data["llms_full_txt"], pages)
            return

        llms_txt = generate_llms_txt(pages)
        llms_full_txt = generate_llms_full_txt(pages)
        self.cache.set(url, llms_txt, llms_full_txt, pages)

        with self.lock:
            if url == self.current_url:
                self.version += 1