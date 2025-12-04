import random
import requests
from requests.exceptions import TooManyRedirects, Timeout, RequestException
from tenacity import retry, stop_after_attempt, wait_exponential
from bs4 import BeautifulSoup
from .config import USER_AGENTS, ACCEPT_LANGUAGES, REQUEST_TIMEOUT, MAX_CONTENT_LENGTH

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

def _build_headers():
    """Build randomized HTTP headers for crawling."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

def _fetch_with_playwright(url):
    """Fetch HTML using Playwright for JavaScript-heavy sites"""
    if not PLAYWRIGHT_AVAILABLE:
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(2000)
            html = page.content()

            browser.close()
            return html
    except Exception as e:
        print(f"Playwright fetch failed: {e}")
        return None

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def fetch_html(url, use_js=False):
    """
    Fetch HTML for a URL with retries.

    Uses requests by default, optionally falling back to Playwright for
    JS-rendered sites. Returns None on non-HTML, oversized, or failed responses.
    """
    # if js rendering is requested and available, use Playwright
    if use_js and PLAYWRIGHT_AVAILABLE:
        html = _fetch_with_playwright(url)
        if html:
            return html
        # fall back to requests if Playwright fails

    headers = _build_headers()

    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True, stream=False)
    except (TooManyRedirects, Timeout, RequestException):
        return None

    # retriable failure
    if resp.status_code >= 500 or resp.status_code in (429,):
        resp.raise_for_status()
    if resp.status_code != 200:
        return None

    ctype = resp.headers.get("Content-Type", "").lower()
    if "text/html" not in ctype:
        return None
    clen = resp.headers.get("Content-Length")
    if clen is not None:
        try:
            size = int(clen)
            if size > MAX_CONTENT_LENGTH:
                return None
        except ValueError:
            pass

    if resp.encoding is None or resp.encoding == 'ISO-8859-1':
        resp.encoding = resp.apparent_encoding or 'utf-8'

    try:
        html = resp.text

        # auto-detect if page needs JS rendering
        if not use_js and _needs_js_rendering(html):
            return fetch_html(url, use_js=True)

        return html
    except (UnicodeDecodeError, AttributeError):
        try:
            return resp.content.decode('utf-8', errors='ignore')
        except:
            return None

def _needs_js_rendering(html):
    """Detect if a page likely needs JavaScript rendering"""
    if not html or len(html) < 500:
        return True

    js_indicators = [
        'ng-view',  # AngularJS
        'ng-app',   # AngularJS
        'data-reactroot',  # React
        'data-react-helmet',  # React
        '__NEXT_DATA__',  # Next.js
        'nuxt',  # Nuxt.js
        'v-app',  # Vue.js
        'id="root"',  # React/SPA common pattern
        'id="app"',   # Vue/SPA common pattern
        '<div id="root"></div>',  # Empty React root
        '<div id="app"></div>',   # Empty Vue root
    ]

    html_lower = html.lower()
    if any(indicator.lower() in html_lower for indicator in js_indicators):
        if 'id="root"' in html_lower or 'id="app"' in html_lower:
            soup = BeautifulSoup(html, 'html.parser')
            body = soup.body
            if body:
                text_content = body.get_text(strip=True)
                # likely a js-rendered
                if len(text_content) < 200:
                    return True
        else:
            return True

    return False