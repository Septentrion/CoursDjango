# Modèles hiérarchques

## Introduction

Puisque les modèles sont des classes, elles peuvent se comporter comme telles et donc être hiérarchisées.

Comme Python admet l'héritage multiple, il même possible dans Django de créer des modèles qui héritent de plusieurs parents.

Il y a trois styles d'héritage possibles dans Django.

1. Souvent, vous voudrez simplement utiliser la classe parent pour contenir des informations qui vous ne voulez pas avoir à taper pour chaque modèle enfant. Cette classe est’t il sera jamais utilisé isolément, donc la sqlution sera de créer une **classe de base abstraite**.
2. Si vous voulez spécialiser un modèle existant et souhaitez que chaque modèle ait sa propre table de base de données, alors la voie à suivre est **l'héritage multi-tables**.
3. Enfin, si vous voulez seulement modifier le comportement d'un modèle, sans en modifier les champs, vous pouvez utiliser un **proxy**.

## Implémentation

### Les classes abstraites

Les classes abstraites sont considérées comme des ressources partagées.

```python
from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    class Meta:
        # L'option abstract indique que cette classe est invisible
        # du point de vue de la base de données
        # Les tables des sous-classes comprendront les propriétés partagées
        abstract = True

class Reader(CommonInfo):
    phone = models.CharField(max_length=5)

class Employee(CommonInfo):
    office = models.ForeignKey(Office)
```

Le point essentiel est que la classe mère :

1. soit abstraite

2. hérite de la classe `Model`de Django

> [!WARNING]
> 
> Les classes concrères héritent naturellement de la classe imbriquée `Meta`, qui peut être surchargée. Néanmoins, le mécanisme interne de Django fait qur l'option `abstract` est modifée à `False` pour les sous-classes, ce qui est le comportement généralement attendu.

### Héritage multi-tables

Dans certains cas, nous voudrions conserver le modèle parent pour faire des recherches.

Si notre bibliothèque conserve des livres papier et audio, chacun avec leurs caractéristiques propres, nous aurions sans doute envie de pour voir tous les livres de tel auteur sans avoir à faire plusieurs requêtes. Dans ce cas, nous pourrions dire :

```python
#models.py

from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)


class AudioBook(Book):
    speakers = models.ListField(models.CharField(max_length=100))

class PaperBook(Book):
    pages = models.IntegerField()
```

La seule chose que nous avons changée est la suppression de l'option `abstract` dans une classe `Meta`.

Dajngo ajoute alors implicitement une association de type `OneToOneField`  danles classe enfants :

```python
book_ptr = models.OneToOneField(
    Book,
    # Si l'enfant est effacé, alors le parent doit aussi l'être
    on_delete=models.CASCADE,
    # L'association est de type parent/enfant
    parent_link=True,
    # book_ptr est aussi la clef primaire de la table enfant
    # Attention donc à ne pas la redéfinir
    primary_key=True,
)
```

### Proxys

Une troisième méthode consiste à définir une variante d'une classe de modèle, avec pour seule différence des méthodes et non des propriétés. Par exemple :

```python
# models.py

from django.db import models

class Reader(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class NonValidatedReader(Person):
    class Meta:
        proxy = True

    def do_something(self):
        # ...
        pass
```

La classe proxy est signalée en tant que telle avec l'option `proxy`de la classe `Meta`. On lui ajoute ensuite diverses méthodes.

Dans cet exemple, nous souhaitons différencier des lecteurs (`Reader`) et des lecteurs qui ne sont pas encore validés (`NonValidatedReader`). Tous deux ont la même structure de données. En revanche, les lecteurs non encore validés interagiron différemment avec l'application, par le biais de méthodes spécifiques.
