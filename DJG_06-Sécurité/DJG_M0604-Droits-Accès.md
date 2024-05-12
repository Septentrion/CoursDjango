# Gestion des droits d'accès

## Introduction

## Permission

La régulation des droits d'accès dans Django repose sur la notion de permission.

Un **permssion** est un objet très simple qui  comporte :

- une action

- un type de contenu

Si `django.contrib.auth` est déclaré dans la variable de configuration `INTALLED_APPS`, tous les modèles du projet bénéficient des quatre permissions de base liées au CRUD : `add`,  `change`, `view`,  `delete`.  Mais il est tout à fait possible de créer ses propres permissions.

### Création d'une permission

#### Dans la définition d'un modèle

La manière la plus simple de créer une nouvelle permission est de la déclarer dans les méta-données des modèles. Nous pourrions vouloir définir une permission d'emprunt pour les lecteurs de la bibliothèque (certains, pour diverses raisons, n'ont pas le droit d'emprunter). Voici comment cela pourrait être implémenté :

```python
# library/models.py

class Book():
    # ... 

    class Meta :
        # Chaque permission est un tuple contenant :
        # - le code de la permission
        # - le nom (textuel) de la permission
        permissions = [('can_borrow', 'Can borrow')]
```

#### Dynamiquement

Il est bien sûr également poissible de définir une permission dynamiquement. Nous pourrions écrire :

```python
from library.models import Book
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(Book)
permission = Permission.objects.create(
    codename="can_borrow",
    name="Can borrow",
    content_type=content_type,
)
```

### Attribution d'un permission

L'attribtui d'une persmission à un utilisateur peut se faire de plusiers manières.

La manière la plus simple est de passer par l'interface d'administration, où vous trouverez des formulaires pout gérer tous les droits d'accès.

Néanmoins, vous aurez peut-être envie d'attribuer certains droits lors de la création du profil utilisateur. Il est donc possible de faire cela par programme, comme ici :

```python
from library.models import Book
from users.models import LibraryUser
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

fred = LibraryUser.objects.get(email="fred@gmail.com")

# Lecture del l'objet `Permission`
content_type = ContentType.objects.get_for_model(Book)
borrowing = Permission.objects.get(
   codename='can_borrow',
   content_type=content_type,
)

# Ajout de la permission
fred.user_permissions.add(borrowing)
fred.save()
```

Chaque utilisateur maintient une liste de permissions, via `user_permissions`, que l'on peut gérer avec les méthodes :  `set`, `add`, `remove`, `clear`.

#### Vérifier une permission

Chaque modèle comprenant les permissions de base du CRUD, nous pouvons vérifier si un utilisateur possède ces permissions avec les méthodes : `has_<action>_permission()`.

## Groupes

Les groupes sont les objets qui permettent d'attribuer à un ensemble d'utilisateurs un ensemble de droits d'accès.

Les groupes sont encore plus simples que les permissions puisqu'il comportent juste ;

- un nom

- une liste de permissions.

Les groupes sont généralement  gérés dans l'interface d'administration.

### Attribution d'un groupe à un utilisateur

Comme pour les permission, chaque utilisateur maintient la liste des groupes auxquels il appartient, via la p^rorpiété `groups`. Il et donc très simple de modifier cette liste avec les mthodes : `set`, `add`, `remove`, `clear`. Par exemple :

```python
from users.models import LibraryUser
from django.contrib.auth.models import Group


fred = LibraryUser.objects.get(email="fred@gmail.com")

# Lecture del l'objet `Group`
librarian = Group.objects.get(
   name='Librarian'
)

# Ajout de la permission
fred.groups.add(librarian)
fred.save()
```

L'utilisateur `fred` bénéficie désormais de tous les droits associés au groupe `Librarian`.

> [!WARNING]
> 
> Les permissions sont mises en cache par Django. Toute modification ests donc susceptible de ne pas être prise immédiatement en compte.
> 
> Pour éviter tout problème, il est conseillé de recharger le profil de l'utilisateur afin d'obtenir un objet « _frais_ ».

## Exploitation des droits d'accès

Une fois définis, les droits d'accès peuvent être utilisés dans les vues et les gab   arits d'affichage.

### Les vues

Pour utiliser les permissions dans le vues, le plus simple est de recourir aux décorateurs. Globalement, nous en avons deux à notre disposition.

#### Vérifier la connexion

Dans ce cas, c'est très simple :

```python
# library/views.py

from django.contrib.auth.decorators import login_required

@login_required
def borrow(request):
    pass
```

Le décorateur `login_required` bloquera les utilisateurs non identifiés. Ceux-ci seront renvoyés vers la page de connexion. En cas de succès, ils pourront poursuivre l'exécution de la tâche.

Il est aussi possible de faire cela « manuellement » :

```python
# library/views.py

def borrow(request):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    # ...
```

### Vérification des permissions

Pour la vérification des permissions, nous pouvons utiliser un autre décorateur :

Dans ce cas, c'est très simple :

```python
# library/views.py

from django.contrib.auth.decorators import permission_required

@permission_required("library.can_borrow", raise_exception=True)
def borrow(request):
    pass
```

Le décorateur `permission_required` bloquera les utilisateurs qui ne sont pas autorisés à emprunter des livres. L'option `raise_exception` engendrera une erreur 403 PERMISSION DENIED.

> [!NOTE]
> Notes la syntaxe de la permission. son code est préfixé du nom de l'application.

### Autorisation selon un test de validité

Les droitd d'accès selon les rôles, les groupes, les permissions ne sont pas toujours suffisants. On a souvent besoin de droits liés à un objet précis  ou des critères de granumlarité très fine.

Dans ce cas, il existe un troisième décorateur, assez générique :

```python
# library/views.py

from django.contrib.auth.decorators import user_passes_test

def limited_borrow(user):
    # Si le nombre de livres djà emprunté par l'utilisateur est >= 5
    # on ne peut plus emprunter le livre supplémentaire.
    return length(user.borrowed) < 5

@user_passes_test(limited_borrow)
def borrow(request):
    pass
```

#### Autorisation sur une instance d'objet

Il est possible aussi de placer des règles d'accès sur les instances de modèles en implémentant les méthodes correspondantes.

Par exemple :

```python
# comment/models


class Comment(models.Model):

    def can_delete(self, user):
        return user == self.author
```

## Ressources

- [Code source des modèles liés à la sécurité](https://github.com/django/django/blob/main/django/contrib/auth/models.py)

- [Code source des décorateurs de sécurité](https://github.com/django/django/blob/main/django/contrib/auth/decorators.py)
