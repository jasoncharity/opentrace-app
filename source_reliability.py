from urllib.parse import urlparse

SOURCE_RELIABILITY = {
    "bbc.co.uk": "A - Highly Reliable",
    "reuters.com": "A - Highly Reliable",
    "theguardian.com": "B - Reliable",
    "telegraph.co.uk": "B - Reliable",
    "order-order.com": "C - Mixed Reliability",
    "twitter.com": "D - Unverified",
    "reddit.com": "D - Unverified",
    "haveibeenpwned.com": "A - System Verified",
    "default": "C - Unknown"
}

def get_source_reliability(url):
    if not url:
        return SOURCE_RELIABILITY["default"]
    domain = urlparse(url).netloc.replace("www.", "")
    return SOURCE_RELIABILITY.get(domain, SOURCE_RELIABILITY["default"])