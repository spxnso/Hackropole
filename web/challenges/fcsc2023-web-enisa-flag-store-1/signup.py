import requests

# Configuration
URL = "http://localhost:8000"


def signup(username: str, password: str, token: str, country: str):
    return requests.post(
        f"{URL}/signup",
        data={
            "username": username,
            "password": password,
            "token": token,
            "country": country,
        },
    )


def main():
    print(
        "Hackropole - https://hackropole.fr/fr/challenges/web/fcsc2023-web-enisa-flag-store-1/"
    )

    username = input("username> ")
    password = input("password> ")
    token = input("token> ")
    country = input("country> ")

    print("[*] Signing up...")
    r = signup(username, password, token, country)
    print(f"Signup status: {r.status_code}")

    print("Done working. Goodbye!")
    exit(1)


main()
