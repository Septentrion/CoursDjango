# Le modèle de sécurité de Django

## Introduction

Dans cette première partie, nous examinons, les mécanismes natifs de Django pour la gestion des utilisateurs. En effet, Django intègre d'emblée une notion de `User` qui est une première étape dans la gestion de la sécurité.

>  [!NOTE]
> 
> Ce document estr principalement une présentation. Nous allons voir ensuite comment créer nos propres utilisateurs.

## Modèle de sécurité

La sécurité de Django repose sur les notions de `User` (utilisateur) et de `Group` (un groupe réprésentant certains droits d'accès).

### Les utilisateurs

Un `User` est défini par :

| Propriété           | Sémantique                                                 |
| ------------------- | ---------------------------------------------------------- |
| `username`          | un identifiant                                             |
| `passwoerd`         | un mot de passe                                            |
| `email`             | une adresse électronique                                   |
| `first_name`        | un prénom                                                  |
| `last_name`         | un nom de famille                                          |
| `groups`            | la liste des groupes auxquels l'utilsateur appartient      |
| `user_persmissions` | la liste des droits de l'utilisateur                       |
| `is_active`         | drapeau indiquant si l'utilisateur est actif               |
| `is_staff`          | drapeau indquant si l'utilisateur fait partie de l'équipe  |
| `is_superuser`      | drapeau indiquant di l'utilsateur est un super-utilisateur |
| `last_login`        | date de dernière connexion                                 |
| `date_joined`       | date de création du profil                                 |

> [!NOTE]
> 
> Les utilisateurs non identifés sont des instances d'une classe particul!re, `AnonymousUser`, qui est utilisée dans les requêtes web

### Les groupes

Par ailleurs,un groupe est simplement défini par :

| Propriété      | Sémantique                                 |
| -------------- | ------------------------------------------ |
| `name`         | le nom du groupe                           |
| `persmissions` | la liste des droits d'accès liés au groupe |

Django reconnaît par défaut trois groupes d'utilisateurs :

- des utilisateurs de base (identifiés)
- des membres de l'équipe (`staff`)
- des super-utilisateurs (`supersuser`)

### Les permissions

Un permission est un objet qui détermine le droit d'exécuter une action sur un type de contenu. Il est là aussi définiassez simplement comme :

| Propriété      | Sémantique                                                    |
| -------------- | ------------------------------------------------------------- |
| `name`         | le nom (arbitraire) de la permission                          |
| `content_type` | le modèle sur lequel s'exerce ce droit                        |
| `codename`     | un code associé à la permssion (généralement dérivé de `name` |

## Utilisation

Le système de sécurité est fonctionnel d'entrée de jeu.

Vous pouvez par exemple créer un super-utilisateur : 

```bash
./manage.py createsuperuser
```

Django vous demandera quelques informations, et vous aurez en particulier accès à l'interface d'administration « _système_ » de Django.

Vous pouvez également créer des utilisateurs via le la ligne de commande de Django :

```bash
./manage.py shell
```

Cette commande vous donne accès à un REPL dans lequel vous pouvez entrer les instructions suivantes :

```python
# In [1]:
from django.contrib.auth.models import User
# In [2]:
user = User.objects.create_user("john", "lennon@thebeatles.com", "lucy")
```

Vérifiez dans votre base de données que les enregistrements ont bien été créés.

### Interface d'administration

Une autre méthode, plus complète, est d'utiliser l'interface d'administration à laquelle vous avez accès pour créer des utilisateurs.

Pour rappel, dnas le fichier `urls.py` de votre projet, vous devez trouver cecu par défaut :

```python
urlpatterns = [
    path("admin/", admin.site.urls),
]
```

c'est-à-dire la route vers l'interface d'administration « système », à laquelle vous pouvez accéder par l'URL :

```
http://localhost:<port>/admin
```

Dans le tableau de bord, vous verrez à gauche un bloc regroupant le modèle des utilisateurs et le modèle des groupes. 

## Ressources

- [API de sécurité de Django]([django.contrib.auth | Documentation de Django | Django](https://docs.djangoproject.com/fr/5.0/ref/contrib/auth/))
