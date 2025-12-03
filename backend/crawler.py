from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
from .config import MAX_WORKERS, MAX_PAGES
from .fetcher import fetch_html
from .content_extractor import (
    extract_title_and_description,
    extract_links,
    extract_canonical_url,
    extract_main_content_html,
    html_to_markdown_content,
)
from .url_utils import (
    is_same_domain,
    normalize_url,
    extract_section_from_url,
    compute_depth,
)
from .models import PageInfo, CrawlResult


class PageProcessResult:
    def __init__(self, page, discovered_links):
        self.page = page
        self.discovered_links = discovered_links

def _is_optional_url(url):
    """
    deeper paths, archive/tags/search pages = optional
    """
    depth = compute_depth(url)
    lowered = url.lower()
    optional_keywords = ["archive", "tags", "category", "search", "page="]
    if depth >= 3:
        return True
    if any(k in lowered for k in optional_keywords):
        return True
    return False

def _process_single_url(url, root_url):
    html = fetch_html(url)
    if not html:
        return PageProcessResult(page=None, discovered_links=set())

    canonical_url = extract_canonical_url(html, url)
    title, description = extract_title_and_description(html)
    main_html = extract_main_content_html(html)
    markdown = html_to_markdown_content(main_html)
    content_hash = sha256(markdown.encode("utf-8")).hexdigest()
    section = extract_section_from_url(canonical_url)
    depth = compute_depth(canonical_url)
    is_optional = _is_optional_url(canonical_url)

    page = PageInfo(
        url=url,
        canonical_url=canonical_url,
        title=title,
        description=description,
        section=section,
        is_optional=is_optional,
        html=html,
        markdown=markdown,
        content_hash=content_hash,
        depth=depth,
    )
    discovered_links = extract_links(html, canonical_url)
    discovered_links = {
        link for link in discovered_links if is_same_domain(root_url, link)
    }
    return PageProcessResult(page=page, discovered_links=discovered_links)

def crawl_site(start_url):
    """
    bfs crawl through nested websites
    multi-threaded fetching
    """
    start_url = normalize_url(start_url, start_url)
    root_domain_url = start_url

    visited_raw = set()
    seen_canonical = set()
    pages = {}

    queue = deque([start_url])
    while queue and len(pages) < MAX_PAGES:
        batch = []
        while queue and len(batch) < MAX_WORKERS * 2 and len(pages) < MAX_PAGES:
            url = queue.popleft()
            if url in visited_raw:
                continue
            visited_raw.add(url)
            batch.append(url)
        if not batch:
            break

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(_process_single_url, url, root_domain_url): url
                for url in batch
            }
            for future in as_completed(futures):
                result = future.result()
                if not result.page:
                    continue
                page = result.page
                canonical = page.canonical_url

                if canonical in seen_canonical:
                    continue
                seen_canonical.add(canonical)
                pages[canonical] = page
                for link in result.discovered_links:
                    if link not in visited_raw and link not in queue:
                        queue.append(link)

    if not pages:
        raise Exception(
            f"Unable to crawl this website. The site may be blocking automated requests or using anti-bot protection (like Cloudflare). "
            f"Try a different website, or verify the URL is accessible in your browser."
        )

    return CrawlResult(pages=list(pages.values()))