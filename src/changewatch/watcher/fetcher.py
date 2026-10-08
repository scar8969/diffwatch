import re, urllib.request
from bs4 import BeautifulSoup

import hashlib

def fetch(url, selector="", headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "changewatch/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", "ignore")
    if selector:
        soup = BeautifulSoup(html, "html.parser")
        content = normalize(" ".join(el.get_text() for el in soup.select(selector)))
    else:
        soup = BeautifulSoup(html, "html.parser")
        content = normalize(soup.get_text())
    return content, hashlib.sha256(content.encode()).hexdigest()

def normalize(text):
    return re.sub(r"\s+", " ", text).strip()
