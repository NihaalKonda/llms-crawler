from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md
from .url_utils import normalize_url
import re

def _generate_description_from_content(html):
    """Generate a description from visible page text."""
    soup = BeautifulSoup(html, "html.parser")

    #try to find paragraph for content description
    for tag in soup.find_all(['p', 'div'], limit=10):
        text = tag.get_text(strip=True)
        if len(text) > 100 and not any(skip in text.lower() for skip in ['cookie', 'javascript', 'browser']):
            text = re.sub(r'\s+', ' ', text)
            if len(text) > 300:
                text = text[:297] + '...'
            return text

    # fallback: get any text from body
    body = soup.body
    if body:
        text = body.get_text(strip=True, separator=' ')
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 300:
            text = text[:297] + '...'
        if len(text) > 50:
            return text

    return None

def extract_title_and_description(html):
    """
    Extract the page title and description.

    Uses common meta description tags first and falls back to a
    generated description from content if none are found.
    """
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

    # if no meta description found, generate one from content
    if not description:
        description = _generate_description_from_content(html)

    return title, description

def extract_canonical_url(html, fallback_url):
    """
    Returns the normalized canonical href if present, otherwise the
    provided fallback_url.
    """
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.select_one('link[rel="canonical"]')
    href = tag["href"].strip() if tag and tag.get("href") else None
    return normalize_url(fallback_url, href) if href else fallback_url

def extract_links(html, base_url):
    """
    Extract and normalize all anchor hrefs from the page.

    Returns a set of absolute URLs, using base_url for resolution.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        normalized = normalize_url(base_url, href)
        if normalized:
            links.add(normalized)
    return links

def extract_main_content_html(html):
    """
    Extract the main content wrapper from the page.

    Tries common main-content selectors first, then falls back to
    body, then the raw HTML.
    """
    soup = BeautifulSoup(html, "html.parser")

    for selector in [
        "main",
        '[role="main"]',
        "#content",
    ]:
        node = soup.select_one(selector)
        if node:
            return str(node)

    body = soup.body
    if body:
        return str(body)
    return html

def html_to_markdown_content(html):
    """
    Clean HTML and convert it to markdown.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(['script', 'style', 'noscript', 'iframe', 'svg', 'object', 'embed', 'canvas', 'video', 'audio']):
        tag.decompose()
    cleaned_html = str(soup)

    md = html_to_md(
        cleaned_html,
        heading_style="ATX",
        bullets="-",
        code_language="",
    )

    return md