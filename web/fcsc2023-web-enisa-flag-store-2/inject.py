import random
import uuid

import requests
from bs4 import BeautifulSoup

# Configuration
URL = "http://localhost:8000"
SESSION = requests.session()


def field(message: str, optional: bool = False, default: str = "") -> str:
    f = input(message)

    if f == "":
        if optional:
            return default
        print("[-] Required field")
        exit(1)

    if len(f) > 192:
        print("[-] Too long")
        exit(1)

    return f


def signup(username: str, password: str, token: str, country: str):
    return SESSION.post(
        f"{URL}/signup",
        data={
            "username": username,
            "password": password,
            "token": token,
            "country": country,
        },
    )


def login(username: str, password: str):
    return SESSION.post(
        f"{URL}/login",
        data={
            "username": username,
            "password": password,
        },
    )


def flags():
    return SESSION.get(f"{URL}/flags")


def generate_username():
    return "user_" + uuid.uuid4().hex[:8]


def generate_password():
    return f"password_{random.randint(6, 9)}"


def print_rows(html: str):
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.find_all("tr")

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        if cols:
            print(cols)


def main():
    print(
        "Hackropole - https://hackropole.fr/fr/challenges/web/fcsc2023-web-enisa-flag-store-2/"
    )

    print("[+] ALL FIELDS MUST NOT EXCEED 192 CHARACTERS OR IT WILL FAIL")

    username = field(
        "username (optional)> ", optional=True, default=generate_username()
    )

    password = field(
        "password (optional)> ", optional=True, default=generate_password()
    )

    token = field(
        "token (optional)> ", optional=True, default="ohnah7bairahPh5oon7naqu1caib8euh"
    )

    country = field("country> ")

    print(f"[+] Using username: {username}")
    print(f"[+] Using password: {password}")
    print(f"[+] Using token: {token}")

    print("[*] Signing up...")
    r = signup(username, password, token, country)
    print(f"[+] Signup status: {r.status_code}")

    if "error=4" in r.url:
        print("[-] Server rejected: field too long")

    print("[*] Logging in...")
    r = login(username, password)
    print(f"[+] Login status: {r.status_code}")

    print("[DEBUG] Cookies:", SESSION.cookies.get_dict())

    print("[*] Fetching flags...")
    r = flags()

    if r.status_code == 200:
        print("[+] Flags page retrieved")
        print(r.url)
        print(r.text)
        print_rows(r.text)
    else:
        print(f"[-] Failed to fetch flags: {r.status_code}")
        print(r.text)

    print("Adios!")
    exit(1)


main()
