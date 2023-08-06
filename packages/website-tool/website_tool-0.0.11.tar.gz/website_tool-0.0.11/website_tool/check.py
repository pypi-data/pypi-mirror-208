import multiprocessing
from urllib.parse import urlparse
from .extract_links import extract_links
from dataclasses import dataclass
import time
import requests
import typing


@dataclass
class ConnectionEstablished:
    ok: bool
    status_code: int
    occurances: list[str]
    latency: float


@dataclass
class ConnectionFailure:
    error: Exception
    latency: float

Result = ConnectionEstablished | ConnectionFailure


def check(locations: list[str], processes: int = 1) -> dict[str, Result]:
    """
    :params locations: list of uris to use as the basis for the check
    :params processes: number of processes to use
    :returns: dict mapping uris to a Result object
    """
    domains = {urlparse(location).netloc for location in locations}
    urls = {}
    occurances = {location: ["Root"] for location in locations}

    with multiprocessing.Manager() as manager:

        unchecked = manager.dict({location: None for location in locations}) # Acts as a set.
        urls = manager.dict()
        occurances = manager.list([(location, "Root") for location in locations])

        with multiprocessing.Pool(processes) as pool:
            pool.map(check_url, [(unchecked, urls, occurances, domains, id) for id in range(processes)])

        occurances_ = {}

        for (link, origin) in occurances:
            if occurances_.get(link, None) is None:
                occurances_[link] = set()

            occurances_[link].add(origin)

        occurances = occurances_
        result = {}

        for url in urls:
            response = urls[url]["response"]

            if isinstance(response, Exception):
                result[url] = ConnectionFailure(response, urls[url]["latency"])
            else:
                result[url] = ConnectionEstablished(response.ok,
                                                    response.status_code,
                                                    occurances[url],
                                                    urls[url]["latency"])

        return result


def check_url(arg):
    unchecked, urls, occurances, domains, id = arg

    while len(unchecked) != 0:
        try:
            url, _ = unchecked.popitem()

            before = time.time()
            response = requests.get(url)
            latency = time.time() - before

            urls[url] = {
                "response": response,
                "latency": latency,
            }

            if not response.headers.get("Content-Type", default = "text/plain").startswith("text/html"):
                continue

        except KeyError:
            continue
        except requests.exceptions.RequestException as e:
            urls[url] = {
                "response": e,
                "latency": time.time() - before
            }

        finally:

            parsed = urlparse(url)

            if parsed.netloc in domains:
                links = extract_links(response.text, domain=parsed.netloc)

                for link in links:
                    occurances.append((link, url))

                    if link not in urls:
                        unchecked[link] = None
