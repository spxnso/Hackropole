---
aliases:
  - fcsc2023-web-chapristi-1
tags:
  - python
  - postgresql
---

# Chatpristi 1/2

> Titre: Chatpristi 1/2  
> Auteur: [Cryptanalyse](https://twitter.com/Cryptanalyse)  
> Difficulté: 1  

## Description

Un ami m&rsquo;a fourni un site pour stocker mes memes, et il me dit qu&rsquo;il y a deux flags cachés dedans. Pouvez-vous m&rsquo;aider à les trouver ?
Pour cette première épreuve, votre but est de trouver un meme caché.
Cette épreuve est composée de deux parties :
Chatpristi 1/2. Chatpristi 2/2. 
## Objectif

Trouver le flag.

## Analyse

Le site est une sorte de gallerie contenant des  memes de chats. Une barre de recherche y est exposé et les images semblent hashés avec SHA-256. 

On pense immédiatemement à une injection SQL, on teste alors simplement le payload

```sql
'test
```

Bingo! Le site nous renvoie une image d'erreur

```sql
pq: syntax error at or near "test"
```

On en apprends donc un peu plus sur son fonctionnement. Il s'agit d'une base de donnée utilisant [PostgreSQL](https://www.postgresql.org/)

On essaye donc de forcer la condition:

```sql
') OR TRUE --
```

Et on trouve le flag (à recopier à la main)

## Flag

FCSC{1D32671928B0DFD5E0B92B57871B1D49}

## Payloads

- [postgresql_injection](../../../payloads/web/postgresql_injection.md)