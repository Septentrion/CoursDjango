# Les sessions dans Django

## Introduction

Comme toute environnement d'application web, Django a besoin de mémoriser des informations concernant la navigation des utilisateurs, notamment un certain nombre de données temporaires. Les **sessions** jouent ce rôle de « *mémoire tampon* ».

Django utilise par défaut un cookie pour conserver la trace de l'utlisateur est lui allouer un espace de mémoire spécifique.

>  [!NOTE]
> 
> Rappelons que, sans ce mécanisme, HTTP étant un protocole sans état, le serveur n'aurait aucun moyen de savoir que deux requêtes successives proviennent du même utilisateur. C'est le principe même des architectures de type **REST**.

## Configuratoin

### Activation des sessions

Dans Django, une session est une partie du « _middleware_ ».

> [!NOTE]
> 
> Dans les architectures en couches, le _middleware_ est la couche qui est chargée de préparer la requête entrante de manière qà ce qu'elle soit interprétable pa la couche suivante (généralement l'application). Le _middleware_ ne traite pas les données mais la forme de la requête. En particulier, c'est souvnet cette qouche qui prend en charge la sécurité et les droits d'accès qux données. Mais elle peut aussi transformer la structure (formelle) des données ou, comme dans le cas des sessions, réactiver des données « _dormantes_ » pour que l'application puisse les traiter.

Pour pouvoir utiliser les mécanisme de session, nous devons déjà vérifier qu'elles sont bine intégrées au _middleware_ de Django :

```python
# libraryproject/settings.py

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Gestionnaire de session 
    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

Normalement, `SessionMiddleware` est configuré par défaut lors de l'installation de Django.

### Stockage des sessions

Djanpo prévoir divers moyens pour gérer les données de session. Vous pouvez trouver le code source des différentes pilotes ici :

- [Pilotes de session](https://github.com/django/django/tree/main/django/contrib/sessions/backends)

#### En base de données

Par défaut, Django stocke les données de session dans la base de données du projet. Dans ce cas, nous avons juste à enregistrer le gesionnaire de session dans les applications installées :

```python
# libraryproject/settings.py

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",

    # Stockage des sessions
    "django.contrib.sessions",

    "django.contrib.messages",
    "django.contrib.staticfiles",
    "sabaki",
]
```

Là aussi, tout devrait être pré-configuré. Lorsque nous exécuterons la commande `./manage.py migrate` la première fois, Django créera la table pour stocker les données de session.

#### Dans un fichier

Pour utiliser un des fichiers, il suffit de l'indiquer dans le fichier de configuration :

```python
# libraryproject/settings.py

# Type depilote utilisé
SESSION_ENGINE = "django.contrib.sessions.backends.file"

# Localisation des fichiers de session
SESSION_FILE_PATH = '/tmp'
```

#### Dans un cache

Django dispose nativement d'un certain nombre d'outils de mise en cache de l'information.

- [Pilotes de caches de Django ](https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-CACHES)

C'est donc un moyen très pratique pour stocker des données de session. D'une manière générale, vouspouvez indIquer à Django quel cache utiliser dans le fichier de configuration :

```python
# libraryproject/settings.py
# Déclaration des caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.RedisCache"
    }
} 

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
```

D'après les recommandations de la documentation officielle, les cas d'utilisation du stockage en cache sont des serveurs comme **Memcache** ou **Redis**. Dans ce cas, vous devrez installer et configurer ces serveurs.

Dans la majrité des cas, néanmoins, la solution du cache en base de données permet une meilleure persistence de données.

#### Dans un cookie

Vous pouvez enfin utiliser des cookies, bien que cela ne soit pas vraiment recommandé. En effet, les cookies ne sont pas chiffrés mais seulement signés

```python
# libraryproject/settings.py

# Type depilote utilisé
SESSION_ENGINE = django.contrib.sessions.backends.signed_cookies

# Protection des cookies contre les attaques XSS
# Très important
SESSION_COOKIE_HTTPONLY = True
```

## Utilisation des sessions

### Vues et requêtes

Lorzque les sessions sont activées (dans la configuration), toute requête HTTP dispose d'une propriété `session` qui nous donne accès aux données de session. 

```python
# library/views.py


def post_comment(request, new_comment):
    """
    Cette fonction permet à un utilisateur de laisser un commnetaire sur 
    la fiche d'un livre. Un même utilisateur ne peut pas commenter deux fois
    le même livre.
    """
    # Y a-t-il une information dans la session ?
    if request.session.get("has_commented", False):
        return HttpResponse("Vous avez déjà laissé un commentaire.")
    c = comments.Comment(comment=new_comment)
    c.save()
    # Mémorisation de l'action de commenter dans la sessions
    request.session["has_commented"] = True
    return HttpResponse("Merci pour votre commentaire !")
```

Le méthodes princip)ales de l'objet `session` sont évidemment :

- `set`: pour inscire une valeur dnas le dictionnaire avec une clef (`has_commented` dans l'exemple) ;
- `get`: pour lire la valeur correspondant à une cler.

Nous pouvons aussi appeler quelques autres méthodes, comme par exemple :

- `clear`: vider la session
- `keys`: liste des clefs de la session
- `items`: liste des valeurs de la session

> [!NOTE]
> Quelques bonnes pratiques sur la gestion des sessions :
> 
> - Utiliser des chaîne caractères Python pour les clefs du dictionaire de session
> - Les clefs qui comment pas un caractères '_' sont réservées à un usage interne de Django
> - Ne surchargez pas l'objet `session`. Utilisez-le comme un simple dictionnaire.
