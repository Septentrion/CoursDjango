# Configuration d'une base SQL

## Introduction

Nous ne traitons ici que de la configuration de l'accès.

L'interaction proprement dite avec la base de données wera traité dans le chapitre sur le requêtes.

## Configuration pour SQL

La configuration d'une base de données se fait dans le fichier `settings.py` dans le dossier spécifique du projet.

Par défaut, Django incorpore une base de données **SQLite**, que l'on peut voir à la racine du projet et qui s'appelle `db.sqlite3`. Il est donc très simple de commencer à travailler sur une application avec des données réelles sans installer ni configurer quoi que ce soit.

Dans `settings.py`, nous trouverons le dictionnaire nommé `DATABASES`, définie ainsi :

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
         "NAME": "db.sqlite3"   
    }
}
```

Naturellement, vous êtes tout à fait libre de changer le nom de la base de données.

### Le pilote

Selon la base de données que vous voulez utiliser (en général, ce sera MySQL, MariaDB ou PostgreSQL) , nous aurons besoin d'un pilote ou d'un adapteur spécifique.

- Pour MySQL/MariaDB 

```bash
pip install mysqladmin
```

- Pour PostgreSQL
  
  ```bash
  pip install psycopg[binary]
  ```

### La configuration

#### MySQL

La configuration de `DATABASES`pour MySQL est la suivante :

```python
# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "OPTIONS": {
            "read_default_file": "/path/to/my.cnf",
        },
    }
}
```

`OPTONS`permet de lire directement un fichier de configuration de MYSQL, en particulier pour récupérer les information de connexion :

```
# my.cnf
[client]
database = NAME
user = USER
password = PASSWORD
default-character-set = utf8
```

Ces informations peuvent également être directement intégrées dans `settings.py` :

```python
# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": <dbname>,
        "USER": <user>,
        "PASSWORD": <password>,
        "HOST": <address>,
        "PORT": <port>,
    }
}
```

#### PostgreSQL

Dans le cas de PostgreSQL, c'est un peu différent, cas nous allons utiliser un *nom de service* :

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "service": "my_service",
            "passfile": ".my_pgpass",
        },
    }
}
```

`my_service` est définidans le fichier de confiouration `.pg_service.conf` :

```text
[my_service]
host=localhost
user=USER
dbname=NAME
port=5432
```

et les identifiants de connexion dans le fichier `.my_pgpass` :

```text
localhost:5432:NAME:USER:PASSWORD
```

## Configuration NoSQL

Pour ce qui concerne les bases de données NoSQL, nous considérons ici principalement **MongoDB** et **Elsaticsearch**, qui sont toutes deux des bases orientées document.

### MongoDB

Pour ce qui concerne MongoDB, il existe encore deux possibilités :

- `pymongo`
- `djongo`
  qui sont deux manières très différentes de se connecter à MongoDB.

#### pymongo

`pymongo` est une bibliothèque très efficace pour intergagir avec MongoDB directement en Python. Pour l'installer :

```bash
pip install pymongo[snappy,gssapi,srv,tls]
# Installer aussi dnspython pour intégrer le protocole mongodb+srv://
pip install dnspython
```

A partir de là, inous devons créer un c:lient qui nous permettra d'accéder à la base de données. Par exemple :

```python
from pymongo import MongoClient
def get_db_handle(db_name, host, port, username, password):

 client = MongoClient(host=host,
                      port=int(port),
                      username=username,
                      password=password
                     )
 db_handle = client['db_name']
 return db_handle, client
```

En général, on installera également `mongoengine` qui est une couche d'abstraction supplémentaire.

#### djongo

`djongo` utilise un mécanisme complètement différent. 

Alors que `pymongo` est nécessite d'écrire les requêtes pour accéder à MongoDB, agit plutôt comme un transpileur qui intègre l'ODM. Ainsi, il est possible d'utiliser la syntaxe native de Django pour écrire requêtes.

Pour l'installer :

```bash
pip install djongo
```

Ensuite, si notre base de données les locale, il suffit de configurer la connexion dans `settings.py` :

```python
DATABASES = {
    "default": {
        "ENGINE": "djongo",
        "NAME": "<dbname>"
}
```

`djongo` offre l'avantage de se servir de la syntaxe de Django, ce qui simplifie l'écriture des requêtes.

### Elasticsearch

Elasticsearch (ES) est un outil qui combine à la fois une base de données document *et* un moteur de recherche « *full text* ». Maintenu par la fondation Apache, il s'intègre en plus dans tout un ecosystème logiciel, généralement connu sous l'acronyme **ELK*, pour :

- **E**lasticsearch (la base de données)

- **L**ogstash (le module pour construire un ETL)

- **K**ibana (une ointerface de visualisation etde requêtage)

De plus, ES s'interface très naturellement avec Python.

Si nous voulons combiner Django et ES, il faut installer le pilote correspondant :

```bash
pip install django-elasticsearch-dsl
```

puis modifier le fichier `settings.py` :

```python
INSTALLED_APPS = [
    # ...
    django_elasticsearch_dsl
]

DATABASES = {
    "default": {
        'hosts: "localhost:9200'
    }
}
```

## Ressources

- [Django et MySQL]()
- [Django et Elasticsearch](https://medium.com/geekculture/how-to-use-elasticsearch-with-django-ff49fe02b58d)
