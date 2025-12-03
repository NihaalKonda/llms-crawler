from urllib.parse import urlparse, urljoin, urlunparse, parse_qsl, urlencode

def get_domain(url):
    parsed = urlparse(url)
    return parsed.netloc.lower()

def is_same_domain(root_url, candidate):
    return get_domain(root_url) == get_domain(candidate)

def normalize_url(base_url, href):
    '''
    normalization - strip fragment, resolve relative urls, normalize cases
    '''
    if not href:
        return ""
    absolute = urljoin(base_url, href)
    parsed = urlparse(absolute)
    parsed = parsed._replace(fragment="")
    query_pairs = [
        (k, v)
        for (k, v) in parse_qsl(parsed.query, keep_blank_values=True)
        if not k.lower().startswith("utm_")
        and k.lower() not in {"ref", "fbclid", "gclid"}
    ]
    cleaned_query = urlencode(query_pairs)

    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    parsed = parsed._replace(query=cleaned_query, path=path)
    return urlunparse(parsed)

def extract_section_from_url(url):
    """
    use first segment in path as seciton name
    """
    parsed = urlparse(url)
    segments = [seg for seg in parsed.path.split("/") if seg]
    if not segments:
        return "Home"
    return segments[0].capitalize()

def compute_depth(url):
    parsed = urlparse(url)
    return len([seg for seg in parsed.path.split("/") if seg])
