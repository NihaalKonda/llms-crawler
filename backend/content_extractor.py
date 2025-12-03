from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md
from .url_utils import normalize_url

def extract_title_and_description(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None

    description = None
    for selector in [
        'meta[name="description"]',
        'meta[property="og:description"]',
        'meta[name="twitter:description"]',
    ]:
        tag = soup.select_one(selector)
        if tag and tag.get("content"):
            description = tag["content"].strip()
            break

    return title, description

def extract_canonical_url(html, fallback_url):
    '''
    try to only look at canonical url for deduplication
    '''
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.select_one('link[rel="canonical"]')
    href = tag["href"].strip() if tag and tag.get("href") else None
    return normalize_url(fallback_url, href) if href else fallback_url

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        normalized = normalize_url(base_url, href)
        if normalized:
            links.add(normalized)
    return links

def extract_main_content_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for selector in [
        "main",
        '[role="main"]',
        ".content",
        "#content",
        ".post",
        ".article",
        "article",
    ]:
        node = soup.select_one(selector)
        if node:
            return str(node)

    body = soup.body
    if body:
        return str(body)
    return html

def html_to_markdown_content(html):
    return html_to_md(
        html,
        heading_style="ATX",
        bullets="-",
        code_language="",
    )