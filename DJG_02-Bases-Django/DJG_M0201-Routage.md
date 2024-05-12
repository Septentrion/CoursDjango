# Le routage avec Django

## Introduction

## Créer les routes

Pour créer les toutes, nous ne devbons pas oubiler que l'application est imbriquée dans un projet (un projet peut héberger plusieurs applications).
Noous allons donc devoir faire deux déclarations.

### Créer les routes de l'application

A la racine de l'application (et non du projet), in touve le fichier `urls.py` qui permet de décrire les routes de l'application.

Une route se définit simplement de manière déclarative, sous forme de liste.

```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

La fonction `path` admet plusieurs paramètres :

1. Le schéma de l'URL
   - Dans l'exemple, la chaîne vide correspnd à la page d'accueil du site
2. La vue correspondante
   - Dans l'exemple, Django cherchera une fonction nommée `index` dans le fichier `views.py`
3. Le nom associé à la route
   - Pour engendrer dynamiquement les URL
4. En option, vous pouvez aussi déclarer des **paramètres nommés** arbitraires (_kwargs_), passé sous forme de dictionnaire.

### Déclarer les routes dans le projet

Pour le moment, nous n'avons pas de moyen d'accéder à la toute que nous venons de créer, car le projet ne sait pas lui-même comment la trouver.
Pour cela, il faut aussi faire une déclaration dan le fichier `urls.py` du projet.

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("shop/", include("shop.urls")),
    path("admin/", admin.site.urls),
]
```

1. La première ligne de la liste déclare le nom de l'application
   - `shop.urls`pointe vers le fichier de routage dans le dossier "`shop`"
   - L'application est maintenant accessible via l'URL : localhost:8000/shop
2. La seconde ligne est une adresse spécifique dont nous reparleons plus loin pour l'interface d'administration

Globalement, `include` peut s'employer dès que vous voulez modulariser vous sytème de routes en définissant un préfixe pour toute une famille de routes.

### Format des URL

Dans la plupart des applications, nous avons des pages dynamiques, liées à des entités d'une base de donnéez, souvent identifiées par une valeur unique.
Pour décrire cela à Django, rien de très comliqué. Dans la déclaration des routes, on spécifie des variables :

```python
# urls.py
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/5/
    path("<int:question_id>/", views.detail, name="detail"),
    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```

### Espaces de noms

Comme nous l'avons dit, un projet Django peut rassembler un nombre indétermoiné d'applications.
Dans ce cas, il est très possible que plusieurs applications déclrent le même nom de route (comme `home`, par exemple).
Pour éviter cela, nous conseillons de toujours définir un espace de noms pour chaque application, sous la forme d'une variable `app_name` :

```python
from django.urls import path
from django.urls import include, path

app_name = 'shop'
urlpatterns = [
    path("shop/", include("shop.urls")),
    path("admin/", admin.site.urls),
]
```

## Ressources

- []()
