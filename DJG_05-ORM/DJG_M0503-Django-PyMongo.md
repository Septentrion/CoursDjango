# Django et PyMongo

## Introduction

## PyMongo
### Installation

Pour pouvoir utiliser **PyMongo**, nosu devons installer le paquetage :

```bash
# L'adapteur pour MongoDB
pip install pymongo

# La bibliothèque pour pouvoir utiliser le protocole `mongdb+srv'
# utile pour se connecgter à Cloud Atlas ou une base protégée par identification
pip install dnspython
```

### Configuration

PyMongo est une bibliothèque Python et n'est pas, de ce fait, pleinement intégrée à Django. Nous utiliserons donc PyMongo comme dans m'importe quel autre projet Python.

#### Déclaration

Dans la perspective d'une certaine homogénéité du code, nous pouvons toutefois conserver la configuration de la connexion dans le fichier `settings.py` :

```python
# settings.py

DATABASES = 
    # ...
}
```

#### Import

La deuxième étape consiste à initialiser la connexion à MongoDB. Là aussi, les choses sont assez simples. PyMongo fournit une classe `MongoClient` qui se charge des communications.

Tout d'abord, nous importons les données de configuration, grâce au module `settings` de Django.

```python
# views.py

from django.conf import settings as conf_settings
db_settings = conf_settings.DATABASES
```

Il suffit ensuite de créer la connexion avec `MongoClient` :

```python
from pymongo import MongoClient

def mongodb_handle(db_name, host, port, username, password):
    """
    Connecteur à la base de données MongoDB
    """
    client = MongoClient(
        host=host,
        port=int(port),
        username=username,
        password=password
    )

    # La connexion à une base de données spécifique pourrait être facultative
    # Ce n'est pas le rôle du connexteur de choisir une base particulière
    db_handle = client['db_name']

    return db_handle, client


database_name = db_settings['mongodb']['NAME']
host = db_settings['mongodb']['HOST']
port = db_settings['mongodb']['PORT']
username = db_settings['mongodb']['USER']
password = host = ['mongodb']['PASSWORD']


database, client = mongodb_handle(database_name, host, port, username, password)

# Finalement, choisir une collection dans la base de données
# On peut utiliser indiofféremment la syntaxe 'objet' ou la syntaxe 'dictionnaire'
books = database.books
```

Nous avons maintenant pour toutes nos vues un objet qui nous permet de converser avec la base de données.

> [!NOTE]
> Nous intégrons pour l'exemple le connecteur dans `views.py`, mais, dans la réalité, il vaudrait mieux créer un module séparé.

### Requêtes

Comme noous l'avons fait remarquer plus haut, PyMongo est indépendant de Django. Sa syntaxe sera celle de MongoDB.

#### Insertion

##### insert_one

Un document est un simple dictionnaire Python. Par exemple :

```python
a_book = {
    'title': "Les Misérables",
    'abstract': "Un ancien bagnard devient un bienfaiteur",
    'identifier': "RVH258",
    'available': True,
    'tags': ['roman', 'révolution', 'exploitation', 'bourgeoisie', 'religion', 'humanisme']
    # ...
}
```

Pour l'enregistrer dans la base de données :

```python
# L'insertion se fait via la collection
# Il est possible de récupérer l'id du document une fois l'enregistrement effectué
books.insert_one(a_book).inserted_id
```

##### insert_many

Dans de nombreux cas, il sera nécessaire d'importer « _en masse_ » des documents. On peut alors faire la même chose que précédemment avec `insert_many`

```python
books.insert_many([book_1, book_2, book_3, book_4]).inserted_ids
```

#### Lecture

Pour lire des documents enregistrés dans MongoDB, nous aurons recours aux techniques traditionnelles de requêtes MongoDB. Soit =

- `find` pour obtenir une liste de documents selon des critères de recherche
- `aggregate` pour faire de l'agrégation de documents.

##### find

La syntaxe de `find` respecte celle de MongoDB. Ony trouve principalement une liste de critères et une projetction.

> cf. la [documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.find) pour la liste comlète de paramètres 

Voici quelques exemples de requêtes :

```python
# Trouver le premier livre
# Nous supposons que nous nous adressons à la collesction `books`
book.find_one()

# Trouver un livre d'après sont id (système)
# Attention, les ids sont des _objets_ et non des chaînes de caractères
from bson.objectid import ObjectId
book.find_one({'_id': ObjectId(<id>)})

# Trouver le premier livre correspondant à un critère :
book_find_one({'available': True})

# Trouver tous les livres
book.find()

# Trouver tous les livres disponibles à l'emprunt
book_find({'available': True})

# Naturellement, toutes les syntaxe MongoDB sont applicables
# Trouver tous les libres acquis après une certaine date
from datetime import datetime
acq_date = datetime(2022, 1, 1)
book_find({'acquisition_date': {'$gt': acq_date}})
# En ajoutant une projection
book_find({'acquisition_date': {'$gt': acq_date}}, {'_id': 0, 'title': 1, 'abstract': 1})
```

`find` retourne un objet du type `Cursor`qui, très classiquement, permet d'itérer sur les résultats de recherche.

> [Documentation pour les curseurs](https://pymongo.readthedocs.io/en/stable/api/pymongo/cursor.html#pymongo.cursor.Cursor)

De la même manière, `aggregate` suit la syntaxe de MongoDB. La manière la pluys pratique de faire est donc de construire un _pipeline_, puis de l'exécuter, comme ainsi :

```python
from bson.son import SON
pipeline = [
    {"$unwind": "$tags"},
    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
    {"$sort": SON([("count", -1), ("_id", -1)])},
]

tags_stats = books.aggregate(pipeline)
```

`aggegate`rend un objet du type `CommandCursor` 

> [Documentation pour les curseurs de commande](https://pymongo.readthedocs.io/en/stable/api/pymongo/command_cursor.html#pymongo.command_cursor.CommandCursor)

#### Autres commandes

PyMongo fournit de nombreux autres outils pour interagir avec MongoDB, qui dépassent l'objet de cette introduction et qui seront examinés à part.

#### Conclusion

PyMongo est l'outil de base qui permet de communiquer avec MongoDB dans un programme Python, quel qu'il soit. C'est une bivliothèque de « _bas niveau_ », qui reproduit fidèlement le comportement d'une base de données MongoDB.
La limite d'un tel outil est qu'il ne s'intègre pas vraiment dans des environnement de « _haut niveau_ » comme Django. Les résultats fournis par PyMongo sont des dictionnaires Python qu'il faut ensuite traduire pour les rendre compatibles avecnotre modèle (et inversement, d'ailleurs).

## MongoEngine

Si nous voulons dépasser les limites naturelles de PyMongo, il est possible d'intéger un ODM (**O**bject **D**ocument **M**apper) qui ajoutera ne couche d'abstraction au-dessus de PyMongo.

### Installation

L'installation de MongoEngine se fait tout simplement via `pip` :

```bash
pip install mongoengine
```

### Configuration

Comme pour PyMongo, MongoEngine est une outil générique. Il ne s'intègre que partiellement à Django. Nous sommes donc tenus de procéder comme précédemment et de connecter manuellement le projet (ou l'application) au serveur de base de données.

```python
from mongoengine import connect

database_name = db_settings['mongodb']['NAME']
host = db_settings['mongodb']['HOST']
port = db_settings['mongodb']['PORT']
username = db_settings['mongodb']['USER']
password = host = ['mongodb']['PASSWORD']


connect(database_name, host, port, username, password)
```

Nous nous retrouvons maintenant dans un contexte plus simple d'utilisation.

### Modèles

MongoEngine apporte à Django des types de propriétés adaptés à la gestion des documents, comme `ListField`, `EmbeddedField` ou `DictField`.
Les types de propriétés natifs de Django sont également redéfinis, à l'instar de `StringField`.
Nous pouvons redéfinir nos livres de cette manière :

```
# models.py

from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField, EmbeddedDocumentListField

class Book(Document):
    'title': StringField(),
    'abstract': StringField(),
    'identifier': StringField(),
    'acquisition_date': DateTimeField(),
    'available': BooleanField,
    'tags': ListField(StringField())
    'borrowed': EmbeddedDocumentListField(Borrow)
```

> [Liste de type de propriétés de MongoEngine](https://docs.mongoengine.org/guide/defining-documents.html#fields)

#### Références

Point très important pour MongoDB, MongoEngine défint également la notion de **référence**, c'est-à-dire de document existant dans une autre collection. Ceci ser tout particulièrement utilse pour les auteurs :

```
class Book():
    'title': StringField(),
    # ...
    'authors': ListField(ReferenceField(Author))
```

> [!NOTE]
> 
> Pour éviter la baisse des performances dues à la multiplication des requêtes entraînées par les références, il est conseillé d'utiliser `LazyReferenceField`, qui n'accède aux document que si cela est nécessaire.

En général, il sera nécessaire de préciser le type de **cascade** que vous voulez appliquer en cas de suppression du document référencé. En effet, la référence peut, dans ce cas, devenir invalide. Plusieurs choix s'offrent à nous :

| Option       | Code | Effet                                                      |
| ------------ | ---- | ---------------------------------------------------------- |
| `DO_NOTHING` | 0    | Ne rien faire (par défaut)                                 |
| `NULLIFY`    | 1    | La référence prend pour valeur `null`                      |
| `CASCADE`    | 2    | Le document supportant la référence est supprimé lui aussi |
| `DENY`       | 3    | La suppression est interdite                               |
| `PULL`       | 4    | Tire la référence d'une liste de références [sic ?]        |

## Ecriture

Ecrire dans la base de données est maintenat trivial, comme cela létati dans les cas de l'ORM de Django avec les bases relarionnelles :

```python
book= Book(title="Fear and Loathing in Las Vegas")
book.save()
```

#### Cas des références

Si le document que vous voulez sauvegarder, comme c'est le cas pour nos livres, contient des références, `save()` n'appliquera pas les changements aux documents référencés, par défaut. Nous devrons forcer le paramètre `cascade`.

```python
book.save(cascade=True)
```

### Consultation

Pour consulter notre base de données bibliothécaire avec MongoEngine, nous allons là aussi retrouver une syntaxe identique à celle de l'ORM de Django, avec un catalogue d'opérateurs un peu moins riche.

>  [Liste de opérateurs de MongoEngine](https://docs.mongoengine.org/guide/querying.html#query-operators)

Globalement, nous allons pouvoir appliquer les même recettes :

```python
# Tous les livres dont le titre commence par 'Les'
Book.objects(title__statswith="Les")
```

### Requêtes complexes

Dans les cas plus complexes, nous pouvons utiliser les « Q functions », comme dans l'ORM, ou chaîner les filtres sur des `QuerySet`.

### Agrégation

Le cas de l'agrégation est un peu différent. Il existe quelques fonctions simples :

```python
# Dénombre tous les livres
Book.objects.count()
# Compter tous les livres disponibles
Book.objects(available=True).count()
# Somme des pages de tous les livres
Book.objects.sum('pages')
# Age moyen des persones inscrites
Reader.objects.average('age')  
```

Néanmoins, donc la plupart des cas, nous aurons besoin de nous référer à l'API native de MongoDB, comme dans le cas de ¨PyMongo :

```python
# Défoinition d'un pipeline d'agrégation
pipeline = [
    {"$sort" : {"title" : -1}},
    {"$project": {"_id": 0, "name": {"$toUpper": "$title"}}}
    ]

# Résultat
books = Book.objects().aggregate(pipeline)

```

### Conclusion


## Ressources

- [Documentation de PyMongo](https://pymongo.readthedocs.io/en/stable/index.html)
- [Documentatio de MongoEngine]()
- [Code source de PyMongo](https://github.com/mongodb/mongo-python-driver)
- [Code source de MongoEngine](https://github.com/MongoEngine/django-mongoengine)
