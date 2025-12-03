class PageInfo:
    def __init__(
        self,
        url,
        canonical_url,
        title,
        description,
        section,
        is_optional,
        html,
        markdown,
        content_hash,
        depth,
    ):
        self.url = url
        self.canonical_url = canonical_url
        self.title = title
        self.description = description
        self.section = section
        self.is_optional = is_optional
        self.html = html
        self.markdown = markdown
        self.content_hash = content_hash
        self.depth = depth

class CrawlResult:
    def __init__(self, pages = None):
        self.pages = pages or []

    def add_page(self, page):
        self.pages.append(page)