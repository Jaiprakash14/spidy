"""Web actions - opening URLs and firing search queries in the default browser."""
from __future__ import annotations
import urllib.parse
import webbrowser


def open_url(url: str) -> tuple[bool, str]:
    if not url:
        return False, "No URL given."
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url, new=2)
        return True, f"Opened {url}"
    except Exception as e:
        return False, f"Couldn't open the browser: {e}"


def search(query: str, engine: str = "duckduckgo") -> tuple[bool, str]:
    if not query:
        return False, "What should I search for?"
    q = urllib.parse.quote_plus(query)
    urls = {
        "duckduckgo": f"https://duckduckgo.com/?q={q}",
        "google":     f"https://www.google.com/search?q={q}",
        "bing":       f"https://www.bing.com/search?q={q}",
    }
    return open_url(urls.get(engine, urls["duckduckgo"]))
