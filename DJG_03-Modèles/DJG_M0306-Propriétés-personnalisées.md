# Définir ses propres classes de propriétés

## Introduction

Dans la plupart des cas, les classes depropriétés natives sont suffisantes. Cependant, il peut arriver que l’offre de Django ne réponde pas à toutes vos exigences, ou que vous vouliez utiliser un champ totalement différent de ceux mis à disposition par Django.

Les types de champs intégrés de Django ne gèrent pas tous les types possibles de colonnes de bases de données, mais seulement les plus courants comme `VARCHAR` et `INTEGER`. Pour des types de colonnes moins usités, comme les polygones géographiques ou même des types définis par les utilisateurs du style des [types PostgreSQL personnalisés](https://www.postgresql.org/docs/current/sql-createtype.html), vous pouvez définir vos propres sous-classes de `Field`.

D’un autre côté, vous pourriez avoir un objet Python complexe pouvant être sérialisé d’une manière ou d’une autre dans un type de colonne standard d’une base de données. C’est une autre situation où une sous-classe de `Field` peut vous aider à utiliser cet objet avec vos modèles.

La sous-classe `Field` Django que vous écrivez fournit les mécanismes de conversion entre vos instances Python et les valeurs de base de données ou de sérialisation de diverses manières (il existe par exemple des différences entre le stockage d’une valeur et son utilisation dans une requête). Si tout cela semble un peu compliqué, ne vous inquiétez pas, cela deviendra plus clair dans les exemples ci-dessous. Rappelez-vous seulement que vous allez souvent créer deux classes lorsque vous voulez créer un champ personnalisé :

- La première classe constitue l’objet Python que vos utilisateurs vont manipuler. Ils l’utiliseront comme attribut de modèle, ils liront ses valeurs à destination de l’affichage, et ainsi de suite. Il s’agit là de la classe `Hand` de notre exemple.
- La seconde classe est la sous-classe de `Field`. C’est la classe qui sait comment convertir votre première classe de sa forme utile pour le stockage vers sa forme Python et vice versa.

## Implémentation

### Structure de base d'une classe

Supposons que, pour une raison ou une autre, nous voulions créer un type de propriété pour les adresses postales. Nous l'appellons `AddressField`. Pour simplifier les choses, nous admettons qu'une adresse comporte :

- un numéro

- le nom de la voie

- le nom de la ville

- le code postal

- le nom du pays

Nous passons sous silence toutes les dificultés et variations liées aux siotuations particulières.

Nous aimerions nous en servir ainsi :

```python
classe Person(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    # Une adresse est un bloc d'information cohérent
    address = AddressField()
```

Il faut donc définir une classe, dont la base ressemblera à ceci :

```python
from django.db import models

class AddressField(models.Field):
    description = "Une adresse avec ses différents composants"

    # Le constructeur fait l'essentiel du travail
    def __init__(self, *args, **kwargs):
        Le constructeur de `Field` est appelé systématiquement
        super().__init__(*args, **kwargs)
```

La question à laquelle nous allons devoir répondre est : « *Comment paramétrer la classe pour qu'elle puisse être transposée dans la base de données ?* »

#### Configuration du nouveau type

Nous devons configurer le nouveau type de propriété.

```python
from django.db import models

class AddressField(models.Field):
    description = "Une adresse avec ses différents composants"

    # Le constructeur fait l'essentiel du travail
    def __init__(self, *args, **kwargs):
        self.number
        super().__init__(*args, **kwargs)
```

#### Méthodes

Il existe un jeu de méthodes utilitaires pour configurer les champs de la base de données, ainsi que pour assurer l'écriture et l'extraction des données.

##### db_type

`db_type ` permet de préciser le type du champ de la base de données. Par exemple :

```python
class Person(models.Field):
    def db_type(self, connection):
        return "varchar(255)"
```

La valeur reendue devra être compatible avec la syntaxe du `CREATE TABLE`. Elle peut donc varier en fonction des foournisseurs de bases de données.
Pour nos adresses, nous souhaiterions sans doute utiliser un champ de type `json`, accessible à la fois dans MySQL, MariaDB, PostgreSQL, etc.

##### rel_db_type

Si votre nouveau champ — ce qui n'est pas le cas ici — sert de clef étrangère, cette méthode permet de rendre cohérente la propriété pour laquelle vous déclarez `ForeignKey`.

##### get_prep_value

##### from_db_value

##### to_python

## Ressources

- [Documentation officielle](https://docs.djangoproject.com/fr/5.0/howto/custom-model-fields)
- [API du type `Field`]([Référence des champs de modèle | Documentation de Django | Django](https://docs.djangoproject.com/fr/5.0/ref/models/fields/#django.db.models.Field.get_prep_value))
