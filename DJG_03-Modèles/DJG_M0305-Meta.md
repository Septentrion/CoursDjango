# Les options pour les modèles de Django

## Introduction

Il est possible d'attribuer à chaqe classe de modèle un jeu d'**options de modèle** en recourant à une classe interne nommée `Meta`.

Cette classe permet de définir, globalement, « *tout ce qui n'est oas une propriété* » du modèle.

## Implémentation

### Principe

L'implémentation des options de modèle est très simple. Prenons par exemple une classe `Author`. Nous pouvons l'enrichir de cette manière :

```python
from django import models

class Author(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    birth_date = models.DateField()
    death_date = models.DateField(blank=True)
    biography = models.TextField()

    # classe interne pour les méta-données
    class Meta:
        # Définition d'un ordre de tri pour les auteurs.
        # Toute liste d'auteurs sera triée danc cet ordre,
        # notamment les requêtes sur la base de données
        ordering = ["last_name", "first_name"]
```

Les options concernent principoalement la base de données, les requêtes, la sécurité et l'interface.

### Héritage

Les classes de modèles peuvent être hiérarchisées (cf. M0304). Chaque sous classe hérite donc naturellement des classes internes dont `Meta`.

Nous pouvons très surcharger cette classe en la redéfinissant et nous pouvons également redéfinir certaines options. Par exemple :

```python
# models.py

from django import models

class Person(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    birth_date = models.DateField()
    death_date = models.DateField(blank=True)
    biography = models.TextField()

    # classe interne pour les méta-données
    class Meta:
        # Définition d'un ordre de tri pour les auteurs.
        # Toute liste d'auteurs sera triée danc cet ordre,
        # notamment les requêtes sur la base de données
        ordering = ["last_name", "first_name"]
        abstract = True
        models.Index(fields=["last_name"]),

class Reader(Person):
    # N° d'inscription
    identifier = models.CharField(max_length=10)

    # La classe hérite de la classe `Meta` de `Person`
    # Elle est déclarée pour pouvoir être surchargée
    class Meta(Person.Meta):
        ordering = ["identifier"]
        abstract = False
        models.Index(fields=["last_name", "identifier"]),
```

## Ressources

- [Listes des méta-options](https://docs.djangoproject.com/en/5.0/ref/models/options/)
