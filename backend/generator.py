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

def _extract_key_content(markdown):
    """Extract key content from markdown - formatted as cohesive paragraphs"""
    lines = markdown.split('\n')
    sections = []
    current_section = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('!'):
            continue
        if stripped.startswith('[') and stripped.endswith(')') and len(stripped) < 100:
            continue

        # start new section
        if stripped.startswith('#'):
            if current_section:
                sections.append(' '.join(current_section))
                current_section = []
            sections.append(stripped)
        elif len(stripped) > 30:
            current_section.append(stripped)

    if current_section:
        sections.append(' '.join(current_section))

    return '\n\n'.join(sections[:10])

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

    if home and home.markdown:
        key_content = _extract_key_content(home.markdown)
        if key_content:
            lines.append(key_content)
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
            desc = f": {p.description}" if p.description else ""
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
            desc = f": {p.description}" if p.description else ""
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
        lines.append("---")
        lines.append("")
        lines.append(f"## {p.title or p.canonical_url}")
        lines.append(f"[{p.canonical_url}]({p.canonical_url})")
        lines.append("")
        if p.description:
            lines.append(f"> {p.description}")
            lines.append("")

        formatted_content = _extract_key_content(p.markdown)
        lines.append(formatted_content)
        lines.append("")

    return "\n".join(lines)
