from collections import defaultdict

def _choose_home_page(pages):
    if not pages:
        return None
    candidates = sorted(pages, key=lambda p: p.depth)
    return candidates[0]

def _build_summary(home):
    if home and home.description:
        return home.description
    if home and home.title:
        return f"{home.title} website."
    return "This site provides documentation and information."

def generate_llms_txt(pages):
    home = _choose_home_page(pages)
    summary = _build_summary(home)
    title = home.title if home and home.title else "Website"
    lines = []

    lines.append(f"# {title}")
    lines.append("")
    # blockquote summary
    lines.append(f"> {summary}")
    lines.append("")
    lines.append(
        "This file lists key public pages and sections that language models "
        "can use to understand and navigate the site."
    )
    lines.append("")
    # group by section
    sections = defaultdict(list)
    optional_pages = []

    for page in pages:
        if page.is_optional:
            optional_pages.append(page)
        else:
            sections[page.section].append(page)

    for section_name in sorted(sections.keys()):
        section_pages = sorted(
            sections[section_name], key=lambda p: (p.depth, p.title or p.url)
        )
        lines.append(f"## {section_name}")
        for p in section_pages:
            desc = (
                f": {p.description}"
                if p.description and len(p.description) < 200
                else ""
            )
            link_title = p.title or p.url
            lines.append(f"- [{link_title}]({p.canonical_url}){desc}")
        lines.append("")

    # optional
    if optional_pages:
        lines.append("## Optional")
        optional_pages_sorted = sorted(
            optional_pages, key=lambda p: (p.depth, p.title or p.url)
        )
        for p in optional_pages_sorted:
            desc = (
                f": {p.description}"
                if p.description and len(p.description) < 200
                else ""
            )
            link_title = p.title or p.url
            lines.append(f"- [{link_title}]({p.canonical_url}){desc}")
        lines.append("")

    return "\n".join(lines)

def generate_llms_full_txt(pages):
    home = _choose_home_page(pages)
    summary = _build_summary(home)
    title = home.title if home and home.title else "Website"

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> {summary}")
    lines.append("")

    #sort pages in order of priority
    sorted_pages = sorted(
        pages,
        key=lambda p: (p.depth, p.title or p.url),
    )
    for p in sorted_pages:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## {p.title or p.canonical_url}")
        lines.append("")
        lines.append(f"[{p.canonical_url}]({p.canonical_url})")
        lines.append("")
        if p.description:
            lines.append(f"> {p.description}")
            lines.append("")
        lines.append(p.markdown.strip())
        lines.append("")

    return "\n".join(lines)
