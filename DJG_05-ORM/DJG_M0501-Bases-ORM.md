# Bases de l'ORM de Django

## Introduction

## Modèles et ORM

## Premières requêtes

### Modification de la base de données

L'ORM simplifie considérablement l'écriture de données dans la base de données.

```python
from library.models import Book


# Création d'un nouveau livre
book = Book(title="Ferdidurke")

# Enregistrer le livre
# Attention : `save()` ne retourne aucune valeur
book.save()

# Oups ! Une erreur typographique...
book.title = "Ferdydurke"
book.save()

# Effacement du livre
book.delete()
```

Comme nous le voyons, avec Django comme avec tous les ORM, la principale difficulté consiste à écrire les requêtes de **consultation** de la base de données

### Consultation

Pour consulter les données, Django à recours à un `Manager`, dont le rôle est, notamment, de construire les résultats de requête, en général sous la forme d'un objet nommé `QuerySet`.

Tout modèle a un acc!s direct au `Manager` via la propritété `objects`.

```python
manager = Book.objects
```

Les principales méthodes du `Manager` sont :

- `all()` : retourne toutes les instances du modèle

- `get()` :  retourne une instance correpondant exactement aux valeurs des critères

- `filter()`  : opére une sélection sur une expression logique

- `exclude()` : filtre négativment les instances correspondant aux critères donnés

#### Exemples simples

##### all

Admettons que nous souhaitions récupérer tous les livres, il suffit d'écrire :

```python
books = Book.objects.all()
```

La requête rend un `QuerySet`, ensemble d'objets de la classe `Book`.

##### get

Avec get, nous pouvons trouver le livre ayant un n° ISBM donné :

```python
book = Books.objects.get(isbn='978-2-02-130451-0')
```

> [!WARNING]
> 
> `get` est une méthode qui ne retourne pas un `QuerySet`

##### filter

Avec `filter`, nous avons la posibilité de créer des équations logiques arbitraires, exactement comme nous le ferions avec SQL.

Néanmoins, il faut s'habituer à la syntaxe de l'ORM qui n'est pas habituelle. Par exemple :

```python
# Un titre de livre commençant pas 'Les'
# L'opérateur est lié à la propriété par un double '_'
# Schéma général : <propriété>__<opérateur>
books = Book.objects.filter(title__startswith="Les")
```

Une particularité des `QuerySet`est qu'il peuvent être chaînés. Par exemple, nous pourrions chercehr tous les livres dont le titre commence par 'Les' et publiés en 2020 :

```python
books = Book.objects
    .filter(title__startswith="Les")
    .filter(publication_date__year="2020")
```

L'ORM ne fera pas plusieurs requêtes. Adoptant un comportement **paresseux**, il ne fera l'évaluation que lorsque cela sera nécessaire, par exemple, pouafficher les résultats :

```python
# Evaluation du QuerySet à ce moment du programme
for b in books:
    print(b.title)
```

###### exclude

`exclude`fonctionne comme `filter`. Si nous voulions les livres dont le titre commence par 'Les', sauf ceux dont l'éditeur est 'Gallimard', alors :

```python
books = Book.objects
    .filter(title__startswith="Les")
    .exclude(publisher__exact="Gallimard")
```

##### Autres méthodes

L'API de `QuerySet` offre bien d'autres possibilités que nous n'évoquerons pas ici, mais qui permettent des requêtes proches de SQL. A titre d'exemple :

```python
# Faire un UPDATE pour marquer tous les livres comme disponibles si le titre contient une chaîne de caractères invalide
Entry.objects.filter(title__regex=r"[aeiouy]{5,10}").update(available=False)
```

### Exemples plus complexes

L'ORM de Django sait opérer sur les relations.  CEla sui la même syntaxe que précédemment.

Si nous voulons tous les livres rangés dans la catégorie 'Roman', sachant que `Category` est un modèle séparé, nous pouvons écrire :

```python
novels = Book.objects.filter(category__name__exact="Roman")
```

Ce qui correspond à une jointure SQL. Et nous pouvpns demander l'inverse :

```python
novels = Category.objects.filter(book__title_contains="routard")
```

Et si nous cherchons tous les romans dont l'auteur a pour nom 'Hugo', nous pourrions écrire :

```python
hugo = Category.objects(name="Roman", book__author__name="Hugo".)
```

Nous avons parcouru ici deux relations : `Category`-> `Book` -> `Author`. 

##### Subtilités syntaxiques

Nous avons vu deux syntaxes pour cumuler des critères de recherche :

```python
# Syntaxe 1
books = Book.objects
    .filter(title__startswith="Les")
    .filter(publication_date__year="2020")

# Syntaxe 2
books = Book.objects
    .filter(title__startswith="Les", publication_date__year="2020") 
```

Il se peut que les résultats ne soient pas toujours identiques, notamment dans le cas où la requête opère que des relations. Pour avoir le code QL correspondant, vous pouvez consulter la connexion :

```python
from django.db import connection
print(connection.queries)
```

Attention, cela ne fonctionne que si le projet est en mode `DEBUG` activé.

## Ressources

- [Documentation officielle]()

- [API de QuerySet]()(https://docs.djangoproject.com/en/5.0/ref/models/querysets/)

- 
