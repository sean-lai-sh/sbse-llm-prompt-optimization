import re


def strip_html_tags(html: str) -> str:
    clean = re.sub(r'<[^>]+>', '', html)
    clean = re.sub(r'&amp;', '&', clean)
    clean = re.sub(r'&lt;', '<', clean)
    clean = re.sub(r'&gt;', '>', clean)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'&quot;', '"', clean)
    return clean.strip()
