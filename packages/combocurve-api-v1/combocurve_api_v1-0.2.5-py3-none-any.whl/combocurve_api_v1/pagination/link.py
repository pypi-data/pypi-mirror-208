import re


def get_next_page_url(response_headers: dict) -> str:
    link_header = response_headers.get('Link', "")

    match = re.findall("<([^<>]+)>;rel=\"([^\"]+)\"", link_header)

    for link, rel in match:
        if rel == 'next':
            return link

    return None
