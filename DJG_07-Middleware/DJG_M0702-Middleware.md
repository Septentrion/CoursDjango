# La couche « middleware » dans Django

## Introduction

un composant « *intergiciel* » est un « _plugin_ » qui est particulièrement utilisé dans les architectures en couches (typiquemet « **3-tier**  »).

Le rôle d'un composant intergiciel est de modifier filter à la fois la requête et la reponse, avant que la première ne soit traitée par l'application et que la seconde ne soit renvoyée au client.

Un composant intergiciel ne remplit généralement aucune tâche liée à l'application. Son seul rôle est de manipuler formellemnt les éléments de la requête. On utilise de tels composants pour :

- procéder à une authentification
- Modifier des informations de contexte dans la requête our la réponse
- Vérifier un jeton de sécurité
- lancer un pricessus asynchrone
- Prendre en charge une erreur
- etc.

Les composants de la couche intergicielle csont généralement organisés en chaîne. Une requête passe donc successivment par tous les composants avant d'être traitée par l'application.

## Configuration

Les éléments de la couche intergicielle sont déclarés dans le fichier de configuration `settings.py` :

```python
# settings.py

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

Tous ces éléments constituent une chaîne ; leur ordre a donc une certaine importance. Par exemple, `SessionMiddleware` dépend du fait que `SecurityMiddleware` ait identifié, ou non, l'utilisateur.

## Implémentation

Dans Django, les composants « _intergiciels_ » peuvent être implémentées de deux façons différentes.

- sous dorme de fonction
- sous forme de classe

### Fonctions intergicielles

Dans le cas d'une fonction, le squelette peut être décrit comme dans cet exemple :

```python
def simple_middleware(get_response):
    """
    Le paramètre `get_response` est une fonction
    qui va se composer avec toutes le autres fonctions de ka chaîne

    final_response = h(g(f(request)))
    """
    # Ici, on peut configurer et initialiser la fonction.

    def middleware(request):
        """
        La fonction a exécuter.
        Celle-ci sera toujours appelée avant la vue
        et éventuellement comme étape dans la chaîne des fonctions intergicielles
        """

        # --> Code à exécuter avant que la vue ne soit appelée
        # 'soit au moment de l réception de la requête)

        response = get_response(request)

        # --> Code à exécuter après que la vue a été appelée 
        # (soit au moment de l'envoi de la réponse)

        return response

    return middleware
    ```
```

### Classes intergicielles

Les fonctionnalités peuvent également être implémentées sous forme de classe.

```python
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuration et initialisation de la classe.

    def __call__(self, request):
        # --> Code à exécuter avant que la vue ne soit appelée
        # 'soit au momen de l réception de la requête)

        response = self.get_response(request)

        # --> Code à exécuter après que la vue a été appelée 
        # (soit au moment de l'envoi de la réponse)

        return response
```

En plus du constructeur qui permet d'intialiser l'intergiciel, la méthode de référence est `__call__`, qui est appelée lors ud processus.

### Hooks

Les composants intergiciels de Django admettent des « _hooks_ » pour automatiser les procédures

##### process_view

`process_view`est une fonction qui peut être utilisée pour déclencher l'exécution d'une vue. Elle permet donc de court-circuiter une partie de la chaîne intergicielle. 

Cette fonction peut retourner :

- `None`, dans ce cas, il ne se passe rien et le traitement continu en chaîne jusqu'à la vue

- un objet `HttpResponse`, auquel cas la réponse est envoyée directement au client.

##### process_exception

Cette fonction est exécutée lrosque la vue lève une exception. De la même manière, elle peut renvoyer soit `None`, soit `HttpResponse`. Naturellement, c'est la première occurrence de cette fonction renvoyant une `HttpResponse` qui l'emporte... sachant que, dans ce cas — nous sommes après lexécution de la vue, les composants intergiciels sont parcourus dnas l'ordre **inverse**.

##### process_template_response

 Cette fonction est appelée immédiatement après l'exécution de la vue, dans le cas où celle-ci produit une `TemplateResponse`, généralement par le biais de la fonction `render`.

Cette fonction doit renvoyer un objet qui implémente lui-même la fonction `rendre`, soiut généralement une instance de `TemplateResponse`. 

##### Utilisation

Les hooks peuvent être utilisés à la fois dans la forme fonctionnelle et dans la forme objet des composants intergiciels.

Pour les classes, ce snt simplement des méthodes supplé:mentaires de la classe.

Pour les fonctions — les fonctions étant également des objets, il est possible de leur définr des attributs. Exemple :

```python
def process_view(request, view_func, view_args, view_kwargs):
    pass

def simple_middleware(get_response):

    def middleware(request):
        response = get_response(request)

        return response

    middleware.process_view = process_view

    return middleware
```

## Exemples

Quelques exemples simples d'utilisation des composants intergiciels:

### Accès à un contenu « premium »

Dans ce cas d'utilisation, nous voudrions restreindre l'accès aux ressources à différents types d'utilisateurs. Pour simplifier, considérons que nous avons des utlisateurs anonymes, des utilisateurs inscrits gratuitement et des utilisateurs payants (premium).

Notre chaîne est déjà capable de détecgter les utilisateurs non connectés. En revanche, nous pourrions demander à la couche intergicielle de distinguer les deux uatres cétégories :

```python
# users/middleware/PremiumUserMiddleware.py

from django.http.response import HttpResponseRedirect

class PremiumUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Certaines ressources sont réservées au utilisateurs abonnés
        if request.path.startswith('/premium/'):
            # Pour les utilisateurs non abonnés
            if not request.user.is_authenticated or not request.user.is_premium:
                # Le processus et court-circuité
                # L'utilisateur est renvoyé vers une page spéciale
                return HttpResponseRedirect('/upgrade/')
        # Sinon... le processus continue
        response = self.get_response(request)

        return response
```

### Optimisation

Pour éviter les requêtes excessives, si deux utilisateurs ayant la même ville demandent un accès à la même ressource, on met celle-ci en cache pour éviter de refaire le cycle. On ne traite pas ici de la question du rafraîchissement du cache.

```python
from django.core.cache import cache
from django.contrib.gis.utils import GeoIP


class GeoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.locator = geoIP

    def __call__(self, request):
        ip = request.META['REMOTE_ADDR', None]
        # On géolocalise l'utilsateur d'après son adresse IP
        location = self.locator(ip)['city']
        # On cherche des données dans le cache
        cache_key = f'geocache:{location}:{request.path}'
        response = cache.get(cache_key)
        # Si la réponse n'est pas en cache, on continue le processus
        if not response:
            response = self.get_response(request)
            cache.set(cache_key, response)

        # Si la réponse à été trouvée, c'est elle que l'on rencvoie
        return response
```

### Traitement d'erreur

On reprend ici le cas simple des erreurs personnalisées.

```python
from django.conf import settings
from django shortcuts import render

class FriendlyErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            if settings.DEBUG:
                raise e
            return render(request, "friendly_error.html", {"error": str(e)}, status=500)
        return response
```

Ce cas pourrait aussi typiquement être réalisé avec le hook `process_exception`

```python
from django.conf import settings
from django shortcuts import render

class FriendlyErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_exception(request, exception):
        if not settings.DEBUG:
            return render(request, "friendly_error.html", {"error": str(e)}, status=500)

        return None
```

## Ressources

- [Documentation officielle](https://docs.djangoproject.com/en/5.0/topics/http/middleware/)
- [TemplateResponse et SimpleTemplateResponse](https://docs.djangoproject.com/en/5.0/ref/template-response/)
