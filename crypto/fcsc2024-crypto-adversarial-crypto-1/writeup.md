# AdveRSArial Crypto (Infant)

> Titre: AdveRSArial Crypto (Infant)  
> Auteur: Maxime  
> Difficulté: intro   

## Description

Je viens de suivre un cours sur RSA mais je crois que j&rsquo;ai oublié quelque chose. Il me semble que le prof parlait de deux trucs, mais je ne sais plus exactement quoi. Vous pouvez m&rsquo;aider ?

## Objectif

Trouver l'erreur dans l'implémentation de l'encryption RSA

## Analyse

L'algorithme utilise l'encryption [RSA (Rivest-Shamir-Adleman)](https://fr.wikipedia.org/wiki/Chiffrement_RSA).

On rappelle les principes de l'encryption

### Génération des clés de chiffrements

1. Prendre deux longs nombre premiers $p$ et $q$ 
2. Calculer $n = pq$, avec $n$ le module de chiffrement
3. Calculer la fonction totient $\lambda(n) = \mathrm{lcm}(p - 1, q - 1)$.
4. Prendre un nombre $e$ tel que $1 < e < \lambda(n)$ et $gcd(e, \lambda(n)) = 1$ afin que $e$ et $\lambda(n)$ soient premier entre eux
5. Calculer l'exposant de chiffrement $d$ tel  que $ed = 1 \pmod{\lambda(n)}$

La clé publique est $(n, e)$ et la clé privée est $(n,d)$ 

### Chiffrement

Soit $m$, le message à chiffrer et $c$ le message chiffré

$c = m \pmod{n}$
### Déchiffrement

$m = c^d \pmod{n}$

### Explication

On télécharge donc le script python ainsi que son output, le but est de retrouver le flag.

```python
from Crypto.Util.number import getStrongPrime, bytes_to_long, long_to_bytes

n = getStrongPrime(2048)

e = 2 ** 16 + 1

flag = bytes_to_long(open("flag.txt", "rb").read())

c = pow(flag, e, n)

print(f"{n = }")

print(f"{e = }")

print(f"{c = }")
```

```
n = 22914764349697556963541692665721076425490063991574936243571428156261302060328685591556514036751777776065771167330244010708082147401402002914377904950080486799957005111360365028092884367373338454223568447811216200859660057226322801828334633020895296785582519610777820724907394060126570265818769159991752144783469338557691407102432786644694590118176582000965124360500257946304028767088296724907062561163478654995994205065812479605136088813543435895840276066683243706020091519857275219422246006137390619897086478975872204136389082598585864385077220265194919486850918633328368814287347732293510186569121425821644289329813
e = 65537
c = 11189917160698738647911433493693285101538131455035611550077950709107429331298329502327358588774261161674422351739941120882289954400477590502272629693853242116507000433761914368814656180874783594812260498542390500221519883099478550863172147588922341571443502449435143090576514228274833316274013491937919397957017546671325357027765817692571583998487352090789855980131184451611087822399088669705683765370510052781742383736278295296012267794429263720509724794426552010741678342838319060084074826713065120930332229122961216786019982413982114571551833129932338204333681414465713448112309599140515483842800125894387412148599
```

Ici, le script utilise un seul nombre premier comme module de chiffrement `n = getStrongPrime(2048)`. Le facteur des nombre premiers $p$ et $q$ n'étant pas présent, on pose alors $n = pq$ avec $p = getStrongPrime(2048)$ et $q=1$ 

On calcule donc $\lambda(n)$.

$$
\lambda(n) = \mathrm{lcm}(\lambda(p), \lambda(q))
$$

La [fonction indicatrice de Carmichael](https://fr.wikipedia.org/wiki/Indicatrice_de_Carmichael) renvoie le plus petit exposant $m$ tel que $a^m \equiv 1 \pmod{n}$  pour tout entier $a$ premier avec $n$ 
Dans ce cas particulier, comme $q = 1$, on a:

$$
\lambda(q) = \lambda(1) = 1
$$

Donc le calcul de $\lambda(n)$ se simplifie à:

$$
\lambda(n) = \mathrm{lcm}(\lambda(p), \lambda(q)) = \mathrm{lcm}(\lambda(p),1)
$$

$\mathrm{lcm}(a, b)$ est le plus petit commun multiple, dit $PPCM$ des nombre $a$ et $b$. Comme tout entier est divisible 1, $lcm(a, 1) = a$.

$$
\mathrm{lcm}(\lambda(p),1) = \lambda(p)
$$

On obtient donc:

$$
\lambda(n) = \lambda(p) = n - 1
$$ 

Ici, comme $n$ est directement premier, on peux calculer la clé privée facilement. Il nous suffit donc de suivre le reste à faire, indiqué par Wikipédia.

> calculer l'entier naturel _d_, [inverse modulaire](https://fr.wikipedia.org/wiki/Inverse_modulaire "Inverse modulaire") de _e_ pour la multiplication modulo φ(_n_) et strictement inférieur à φ(_n_), appelé _exposant de déchiffrement_ ; _d_ peut se calculer efficacement par l'[algorithme d'Euclide étendu](https://fr.wikipedia.org/wiki/Algorithme_d%27Euclide_%C3%A9tendu "Algorithme d'Euclide étendu").

On cherche donc $d$ tel que:

$$
ed = 1 \pmod{\lambda(n)}
$$

Donc:

$$
d = e^{-1} \pmod{n - 1}
$$

Autrement dit, il suffit de calculer l'inverse modulaire de $e$ modulo $n - 1$
Une fois $d$ obtenu, on peux simplement déchiffrer en utilisant la formule vue plus tôt $m = c^d \pmod{n}$ puis convertir le résultat en bytes pour obtenir le flag

On automatise le tout dans un script python

```python
from Crypto.Util.number import inverse, long_to_bytes

n = 22914764349697556963541692665721076425490063991574936243571428156261302060328685591556514036751777776065771167330244010708082147401402002914377904950080486799957005111360365028092884367373338454223568447811216200859660057226322801828334633020895296785582519610777820724907394060126570265818769159991752144783469338557691407102432786644694590118176582000965124360500257946304028767088296724907062561163478654995994205065812479605136088813543435895840276066683243706020091519857275219422246006137390619897086478975872204136389082598585864385077220265194919486850918633328368814287347732293510186569121425821644289329813

e = 65537

c = 11189917160698738647911433493693285101538131455035611550077950709107429331298329502327358588774261161674422351739941120882289954400477590502272629693853242116507000433761914368814656180874783594812260498542390500221519883099478550863172147588922341571443502449435143090576514228274833316274013491937919397957017546671325357027765817692571583998487352090789855980131184451611087822399088669705683765370510052781742383736278295296012267794429263720509724794426552010741678342838319060084074826713065120930332229122961216786019982413982114571551833129932338204333681414465713448112309599140515483842800125894387412148599

# Calcul de λ(n)

lambda_n = n - 1

# Calcul de d

d = inverse(e, lambda_n)

# Déchiffrement

m = pow(c, d, n)

flag = long_to_bytes(m)

print(flag)
```

## Flag

FCSC{d0bf88291bcd488f28a809c9ae79d53da9caefc85b3790f57615e61c70a45f3c}
