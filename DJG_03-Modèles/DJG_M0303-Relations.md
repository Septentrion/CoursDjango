# Les relations dans les modèles de Django

## Introduction

Nous venons de voir comment créer des modèles simples. Mais généralement, un modèle est composé d'entités liées les unes aux autres. Par exemple, un livre sera l'œuvre d'un auteur ou sera emprinté par un lecteur. Un lecteur aura lui-même un abonnement, etc. Nous avons déjà ici quatre entités interconnectées.

Comment prence ceci en compte dans notre projet ? Cela va dépendre du type de base de données que nous utilisons.

## Types de relations

De manière canonique, on définit trois types de relations entre entités d'un modèle. Cette classification est globalement commune à toutes le représentations basées sur le **modèle Entité/Association**.

### one-to-one (1-1)

Ce type de releation indique qu'un objet d'une classe est lié à un et un seul objet d'une autre classe. C'est un cas qui n'est oas très courant, mais que l'on trouve typiquement dans les sites de commerce en ligne quand il y a des clients et des paniers : un client à un seul panier et un panier n'appartient qu'à un seul client.

### one-to-many (1-N)

Dans ce type d'association, un objet d'une classe peut être associé à plusieurs objets d'une autre classe, mais l'inverse n'est pas vrai. On oeut par exemple dire qu'un pays contient un certain nombre de villes, mais qu'une ville n'est située que dans un seul pays (à la fois, car cela peut changer).

C'est, au passage, le seulk type d'association qui ne soit pas symétrique. L'association inverse est « *many-to-one* ».

### many-to-many (N-N)

Enfin l'association « *many-to-many* » indique que les deux objets entretiennent des relations multiples. Par exemple, auteur peut avoir écrit plusieurs livres et un livre eut avoir été écrit pasz plusieurs auteurs. C'est également typiquement le cas des réseaux sociaux, où les personnes ont des ensembles d'amis qui ont eux-mêmes des ensembles d'amis.

## Implémentation

Nous allons maintenant examiner les différentes manières d'implémenter ces différents cas de figure.

#### SGBD relationnels

Les bases de données relationnelles sont fondées sur des schémas très structurés, comppés de **tables**, qui entretiennent entre elles des relations par le biais de clefs étrangères.

Un SGBDR comme MySQL sait donc gérer nativement les associations 1-N/N-1

##### many-to-one

C'est la solution la plus simple. Il suffit d'utiliser le type de propriété `ForeignKey`.

```python
# models.py
from django import models

# Une classe pour représenter les catégories de livres : 
# romans, essais, bande dessinée, etc.
class Category(models.Model):
    pass

# Une classe pour les livres
class Book(models.Model):
    title = models.CharField()
    acquisition_date = models.DateField()
    category = models.ForeignKey(Category)
```

L'association inverse n'est pas définie. Elle peut être parcourue, comme nous le verrons grâce aux requêtes de l'ORM de Django.

##### many-to many

Ici, deux cas peuvent encore se présenter, qui tous deux font appel à `ManyToManyField`.

Dans le premier cas, l'assocation est simple, c'est-à-dire qu'elle ne supporte pas d'attribut. Par exemple, des livres et des mots-clefs :

```python
# models.py
from django import models

# Une classe pour représenter les mots-clefs : 
class Keyword(models.Model):
    key = models.CharField()
    description = models.TextField()

# Une classe pour les livres
class Book(models.Model):
    title = models.CharField()
    category = models.ManyToManyField(Keyuword)
```

Remarquons toutefois que l'association n'est définie qu'une seule fois. Il y a donc un « *sens directeur* » et un « *sens inverse* ».

Mais il  existe aussi une seconde possibilité, dans laquelle l'association est « _décorée_ » par des attributs. C'est par exemple ce cas des emprunts. Un lecteur peutr emprunter plusieurs livres et inversement. Toutefois chaque emprunt est associé à des atributs comme la date de retour prévue, la date de retour effective, un commentaire en cas dégradation du livre, etc.

Dans ce cas, la déclaration est plus complexe, car elle nécessite une double déclaration :

```python
# models.py
from django import models

class Reader(models.Model):
    pass

class Book(models.Model):
    title = models.CharField()
    borrowers = models.ManyToManyField(Keyword, through="Borrow")

class Borrow(models.Model):
    borrower = models.ForeignKey(Reader)
    book = models.ForeignKey(Book)
    return_date = models.DateField()
    real_return_date = models.DateField()
    comment = models.TextField()
```

Comme nous le voyons, il faut à la fois :

- déclarer la classe d'association munie de relation *many-to-one* antagonistes ; c‘est finalement la décomposition de l'association *many-to-many* ;

- indiquer dans la classe `Book`que l'association est bien réciproquement multiple ; là aussi, il y a un sens privilégié dans l'association

##### one-to-one

Dans les cas, assez rares, où nous avons besoin de ce type d'association, nous devons avoir recours à un type de propriété `OneToOneField`, qui ne diffère pas des précédents. Nous pourrions voouloire représenter une association entre les employés de la bibliothèque et les bureaux, chaque employé ayant un bureau particulier :

```python
# models.py
from django.db import models

# Class pour les bureaux
class Office(models.Model):
    pass

# Classe pour les employés
class Employee(models.Model):
    #...
    office = models.OneToOneField(Office)
```

## Définition des modèles

Le modèle de données est entièrement défini dans le fichier `models.py`.

Globalement, il se présente ainsi :

```python
# models.py
from django.db import models


class Author(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

Dans le cas où nous utilisons une base de données relationnelles, on voit apparaître une `ForeignKey` qui permettra la liaison entre les tables lors de la création de la base.

### SGBD NoSQL

Si nous utilisons une base de données comme MongoDB, les choses vont être assez différentes puisque :

1. il n'y a pas de schéma (ou alors il est facultatif comme dans Elasticsearch)

2. il n'y a pas (à proprement parler) de jointures, donc de pointeurs entre les collections

Comme nous l'avons expliqué précédemment, utiliser Django avec MongoDB peut se faire de différentes manières.

#### mongoengine

Si nous optons pour `mongoengine`, l‘exemple sur les catégories et les livres pourrait se réécrire ainsi :

```python
from mongoengine import Document, StringField, IntField, EmbeddedDocumentListField

class Category(Document):
    titre = StringField(required=True, max_length=50)
    description = StringField()
    books = EmbeddedDocumentListField(Book)

class Book(Document):
    titre = StringField(required=True, max_length=100)
    contenu = StringField(required=True)
    date_creation = IntField()
    auteur = StringField()
```

Nous voyons qu'il existe une collection `Category` qui contient une liste de `Book` qui sont des sous-documents. Dans ce cas précis, ce n'est peut-être pas ce que nous voudrions faire, car pour consulter les livres, qui sont les objets principaux de motre modèle, nous devrions passer par les catégories. Il serait peut-être plus judicieux de passer par une référence :

```python
from mongoengine import Document, StringField, IntField, ReferenceField

class Category(Document):
    titre = StringField(required=True, max_length=50)
    description = StringField(required=True, unique=True)

class Book(Document):
    titre = StringField(required=True, max_length=100)
    contenu = StringField(required=True)
    date_creation = IntField()
    auteur = StringField()
    category = ReferenceField(Category)
```

Nous nous ramenons ici à quelque chose qui ressemble à une clef étrangère, mais qui est très différente du point de vue interne de la base de données.

Pour les associations *many-to-many*, il suffira de combiner les listes et de références. Dans le cas le plus simple :

```python
# models.py
from mongoengine import Document, StringField, IntField, ListField, ReferenceField

# Une classe pour représenter les mots-clefs : 
class Keyword(models.Model):
    key = StringField()
    description = StringField()

# Une classe pour les livres
class Book(models.Model):
    title = StringField()
    keywords = ListField(ReferenceField(Keyuword))
```

L'inconvénient principal de `mngoengine` est qu'il n'est pas uniforme à Django. Les noms des classes de propriétés sont différentes. Qui plus est, comme nouw le verrons, la syntaxe des requêtes est spécifique.

Il existe une solution alternative.

#### djongo

`djongo` résout les petits problèmes qu nous venons de pointer. C'est en fait une surcouche des modèles de Django, qui ajoute ce qui est nécessaire à MongoDB.

1. les classes de `djongo` portent le même nom que celles de Django, excepté naturellement pour les listes, les documents imbriqués et les références.
2. les requêtes, que nous étudierons plus loin, utilisent la syntaxe de l'ORM de Django

Reprenons les exemples précédents :

```python
# models.py
from djongo import models

# Une classe pour les livres
class Book(models.Model):
    title = models.CharField()
    acquisition_date = models.DateField()

# Une classe pour représenter les catégories de livres : 
# romans, essais, bande dessinée, etc.
class Category(models.Model):
    title = models.CharField()
    description = models.TextField()
    books = ArrayField(EmbeddedModelField(Book))
```

On voit apparaître deux nouveaux types :

- `EmbeddedModelField`, qui représente un type de document imbriqué
- `ListField`, qui indique que l'on peut avoir plusieurs documents imbriqués.

#### Sous-documents ou référence

Une question spécifique aux bases de données orientées document est la question du choix d'architecture. Vaut-il mieux imbriquer des sous-documents au sein d'une même collection ou créer des références entre collection ?

##### Imbrication et localité

Un avantage des sous-documents est la localité de la recherche. Comme les bases document n'ont pas d'opération de jointure, grouper toutes les informations « au même endroit » amène des gains de performance notables. A l'inverse utilser massivment des références pour des consultations fréquentes entraîne des pertes de performance.

##### Imbrication et atomicité

Une seconde raison d'utiliser les sous-documents est le fait que les bases de données document n'ont pa nonplus de notion de transaction. La récupération sur erreur est donc beaucoup plus difficile si un problème survient *pendant* une séquence d'écriture de pluxieurs documents. Si l'on a juste besoin d'une seule opératio pour tout écrire, le problème disparaît.

##### Référence et flexibilité

Inversement, les références introduisent une plus grande flexibilité dans la gestion des informations et une plus grande justesse des requêtes. Imaginez que vous ayez des billets de blogs associés à des commentaires en sous-documents et que vous exécutiez la requête suivante :

```python
db.posts.find(
    {'comments.author': 'Stuart'},
    {'comments': 1})
```

Vous obtiendrez alors toute la « forêt » des billets de blogs avec tous les commentaires, c'est-à-dire beaucoup plus d'information que ce qui vous est utile. Même si la *projection* limitee l'avalanche, vous aurez *a minima* les commentaires de tout le monde en retour.

##### Référence et haute arité

Un autre cas de figure est celui où vous avez beaucoup, voire énormément, de documents liés. Un exemple pire encore est celui de documents récursifs, comme les messages d'un forum. 

Cette situatio pourrait conduire à avoir des documents extrêmement gros, et à avoir un impact très négatif sur le fonctionnement de la base.

1. Tout d'abord parce que les documents dont limités à 16Mo (ce qui n'est certes par rien, mais...)

2. Ensuite parce que MongoDB utilise beaucoup la mémore vive et que plus aurez de documents volumineux, plus vous aurez besoin d'avoir recours au « *swap* » pour mettre de données en cache, ce qui ralentit considérablement le système.

3. Le fait dd'augmenter la taille des documents oblige la base à trouver sur le disque des espaces (contigus) disponibles pour les stocker. Le réarrangmeent des données sur le disque peut lui aussi ^stre extrêmement coûteux.

##### Référence et association N-N

Enfin, un cas insoluble autrement est celui des associations *many-to-many*. Dans ce cas, l'imbrication est tout simplement impraticable puisqu'il faudrait, à chaque modification, mettre à jour toutes les occurrences des sous-documents, sans compter la perte de place sur le disque.

Dans ce cas, la seule solution est de féinir une référence.

##### Conclusion

Les arguments ci-dessus montrent bien pourquoi les bases de données orientées document doivent être utilisées avec des modèles conceptuels de données relativement simples pour lesquels la rapidité d'accès en lecture/écriture leur donne l'avantage sur les systèmes relationnels.

Pour ce qui est de la question posée, il est clair qu'il n'y a pas de réponse définitive. On voit que cela dépendra surtout du volume et de l'importance attachée aux différentes parties du modèle de données. 

## Ressources

- [Sous-doucments MongoDB dans Django](https://django-mongodb-engine.readthedocs.io/en/latest/topics/embedded-models.html) 
