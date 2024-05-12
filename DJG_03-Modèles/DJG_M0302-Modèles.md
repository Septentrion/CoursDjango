# Les modèles de données dans Django

## Introduction

Les **modèles** représentent la le modèle physique des données, vu par l'application. Dans Django, les modèles sont des classes tout à fait classiques  qui sont utilisées da  nas trois grands contextes :

1. comme abstraction du schéma de base de données

2. comme vecteur pour les requêtessur cette base de données

3. comme support pour les formulaires utilisateurs (cf. chapitre 4)

## Définition des modèles

Le modèle de données peut être entièrement défini dans le fichier `models.py`. Contraireme,nt à PHP, il n'y a pas de nécessité à séparer les fichiers, même si cela reste une bonne pratique, en général.

Globalement, il se présente ainsi :

```python
# models.py
from django.db import models

# Classe des livres
class Book(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    pub_date = models.DateTimeField("date published")
    genre = models.ChoiceField(choices=[("R", "roman"), ("E", "essai)])
```

Nous voyons que chaque classe hérite de la classe `Model` de Django (du paquetage `models`).

Les classes de modèles définissent des propriétés, qui sont elles-mêmes des sous-classes de `Field`. Django fournit naturellement une grande variété de types de propriétés, correspondant aux usages des bases de données, mais il est tout à fait possible, comme nous le verrons, de définir nos propres types.

Dans les cas les plus simples, le choix d'un type de base de données n'aura pas de répercussions sur les classes de modèles. Toutefois, comme nous verrons bientôt, dès que des relations sont définies entre les entités du modèle, il en va autrement.

Pour utiliser les modèles, il y a juste deux conditions à remplir :

1. que l'application dans laquelle ils sont définis soit déclarée dans le projet Django

2. que la liaison avec la base de données soit effective

### Notion de migration

Pour que la seconde condition soit remplie, Django propose un système de « *migration* », qui permet de synchroniser la base de données et les classes de modèles du projet.

Il suffit pour cela de passer par la ligne de commandes :

```bash
# Création de la migration
./manage.py makemigrations

# Application de la migration
./manage.py migrate
```

Les migrations sont elles-mêmes des classes qui sont conservées dans le dossier `migrations`à la racine du projet.

Les migrations sont intéressantes par le fait qu'elles permettent une mise à jour incrémentale du schéma de la base de données. Elles visent aussi à mettre en œuvre un versionnage du modèle et donc de pouvoir revenir en arrière sur des versions antérieures du schéma de la base de données.

Naturellement, les migrations ont surtout du sens lorsque nous parlons de bases de données relationnelles. Avec des bases de données orientées document, comme MongoDB, cela est beaucoup moins pertinent.

Dans le cas où nous utilisons une base de données relationnelles, on voit apparaître une `ForeignKey` qui permettra la liaison entre les tables lors de la création de la base.

## Propriétés des modèles

Comme nous l'avons dit, les propriétés sont des classes qui héritent de la classe `Field`. Chaque type de propriété admet un certain nombre d'attributs propres.

Par exemple `CharField` reconnaît l'attribut `max_length`, qui est finalement l'équivalent de la longueur d'un champ `VARCHAR` en SQL.

Tous les types de propriétés reconnaissent une poignée d'attributs, en particulier `blank` et `null`. Ces deux attributs indiquent que l'objet n'est pas obligé d'associer une valeur à la propriété.  Mais :

- `null` indique plutôt que la base de données (relationnelle) admet les valeurs `NULL`

- `blank` indique plutôt qu'une valeur nulle n'invalide pas la validation des formulaires.

D'autres options peuvent s'avérer utiles,  notamment lorsque les modèles sont utilisés pour les formulaires :

| attribut    | rôle                                                        |
| ----------- | ----------------------------------------------------------- |
| `default`   | Valeur par défaut associée à la propriété                   |
| `help_text` | Texte d'aide pour les formulaires                           |
| `unique`    | Contraint les valeurs à être uniques dans la bas de données |

On peut également associer un`verbose_name`, qui est une version longue et « textuelle » du nom de la propriété :

```python
first_name = models.CharField("Prénom de la personne", max_length=30)
```

Il doit être défini, comme ont le voit comme le **premier argument positionnel** du constructeur de l'objet.

## Méthodes des modèles

Comme toute classe, les classes de modèles supportent des méthodes. Celles-ci permettent de définir une interface de la classe indépendante de sa représentation en base de données. Par exemple :

```python
# Classe des livres
class Book(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    pub_date = models.DateTimeField("date published")
    genre = models.ChoiceField(choices=[("R", "roman"), ("E", "essai)])
    language = models.CharField(max_length=5, default="fr_FR")

    @property
    def traduction(self):
        return not self.language == "fr_FR"

    def slug(self):
        return utils.slugify(self.title)
```

Comme nous le voyons dans cet exemple, les mécanismes de Python s'appliquent. `traduction` est ici une propriété qu sens de Python, mais non au sens des modèles Django. Nous pourrions écrire :

```python
book = Book(title="Les Misérables")
# `traduction` est une valeur booléenne publique virtuelle
print(book.traduction)
# `slug` est une méthode qui rend une chaîne d'URL
print(book.slug())
```

## Création et mise à jour de la base de données

### Déclaration du modèle de données

Une fois les modèles créés, nous devrions vérifier que l'application a bien été déclarée à Django. Généralement, on conseille de faire cela dès la création de l'application. Donc :

```python
INSTALLED_APPS = [
    "books",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

`books`étant ici le nom de l'application Django, telle que créée avec la commande `startapp `.

### Migration

Pour rendre les modèles effectifs, nous derons enfin exécuter les migrations correspondantes.

## Organisation des classes

Même si cela n'est pas requis par Django, une bonne pratique est de créer un fdichier par classe (souvent les exemples donnés ne respectent pas ceci, même dans les documents présents par souci de simplicité).

Pour cela, nous allons créer un package `models` à la racine des applications, en remplacement du fichier `models.py`.

Puis nous exporterons toutes les classes dans le fichier __init__.py :

```python
# models/__init__.py

from .book import Book
from .category import Category
# etc.
```

Puis, dans notre code :

```python
from .models import Book, Category
```

## Ressources

- [Les modèles dans Django](https://docs.djangoproject.com/en/5.0/topics/db/models)
- [Les types de propriétés](https://docs.djangoproject.com/en/5.0/ref/models/fields/#field-types)
- [Options des propriétés de modèles](https://docs.djangoproject.com/en/5.0/ref/models/fields/#field-options)
