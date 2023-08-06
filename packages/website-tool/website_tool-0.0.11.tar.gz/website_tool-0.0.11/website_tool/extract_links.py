from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin

TAGS = ["link", "img", "video", "script", "a"]
ATTRS = ["href", "src"]

class Parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag in TAGS:
            url = list(filter(lambda l: l[0] in ATTRS, attrs))

            if len(url) == 1:
                self._urls.add(url[0][1].strip())

    def __init__(self):
        super().__init__()
        self._urls = set()

def handle_relative_link(u, base_uri="", proto="http"):

        result = urlparse("")
        parsed = urlparse(u)
        base = urlparse(base_uri)

        if parsed.scheme == base.scheme:
            parsed = parsed._replace(scheme = "")

        if parsed.scheme != "":
            result = result._replace(scheme = parsed.scheme)
            result = result._replace(netloc = parsed.netloc)
            result = result._replace(path = remove_dot_segments(parsed.path))
            result = result._replace(query = parsed.query)
        else:
            if parsed.netloc != "":
                result = result._replace(netloc = parsed.netloc)
                result = result._replace(path = remove_dot_segments(parsed.path))
                result = result._replace(query = parsed.query)
            else:
                if parsed.path == "":
                    result = result._replace(path = base.path)

                    if parsed.query != "":
                        result = result._replace(query=parsed.query)
                    else:
                        result = result._replace(query=base.query)
                else:
                    if parsed.path.startswith("/"):
                        result = result._replace(path=remove_dot_segments(parsed.path))
                    else:
                        result = result._replace(path=urljoin(base.path, parsed.path))
                        result = result._replace(path=remove_dot_segments(result.path))

                    result = result._replace(query=parsed.query)

                result = result._replace(netloc=base.netloc)

            result = result._replace(scheme=base.scheme)

        result = result._replace(fragment = parsed.fragment)

        return result.geturl()

def remove_dot_segments(path):
    return path #TODO: Implement remove_dot_segments according to RFC 3986

def extract_links(text, domain="", proto="http"):
    parser = Parser()
    parser.feed(text)

    result = parser._urls

    result = { r for r in result if not r.startswith(("mailto", "e-name")) }

    result = { handle_relative_link(u, base_uri=domain, proto=proto) for u in result }

    return result
