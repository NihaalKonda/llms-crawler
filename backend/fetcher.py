import random
import requests
from requests.exceptions import TooManyRedirects, Timeout, RequestException
from tenacity import retry, stop_after_attempt, wait_exponential
from .config import USER_AGENTS, ACCEPT_LANGUAGES, REQUEST_TIMEOUT, MAX_CONTENT_LENGTH

def _build_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def fetch_html(url):
    """
    fetch html content for url with retries on retriable errors
    returns none if content is not html or too large
    """
    headers = _build_headers()

    try:
        session = requests.Session()
        # Set max redirects to 30 (default is 30, but being explicit)
        session.max_redirects = 30
        resp = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    except (TooManyRedirects, Timeout, RequestException):
        # If too many redirects, timeout, or other request error, just return None (skip this page)
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

    return resp.text