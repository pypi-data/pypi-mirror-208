import requests


def unshorten_url(short_url):
    r = requests.head(short_url)
    if r.status_code >= 200 and r.status_code < 400:
        url = r.headers.get("location", None)
        if url is not None:
            return url

    return None
