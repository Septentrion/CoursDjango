# Connecter Djago et MonDB avec Djongo


## Introduction

**Djongo** est **ODM** (Object-Document Mapper) dont le rôle est donc de rendre cohérents les deux modèles de données que sont les objets (de Python) et les documents (de MongoDB).

Un ODM (comme un ORM) a pour fonction de masquer,du point de vue de l'application, les différences de représentation. Nous ne voyons donc que des objets. 
L'ODM se charge de :
- transformer les objets en documents (et inversement)
- assurer que sueles des données cohérentes sont écrites dans la base de données
- conserver la trace des objets qui ont déjà été créés par l'application


## Installation

Pour installer Djongo, rien de plus simple :
```bash
pip install djongo
```

Pour configurer l'application Django, nous devons modifier le fichier `settings.py` =
```python
DATABASES = [
    'default': {
        'ENGINE': 'djongo',
        'NAME': '<nom-de-la-base>'
        # Crée implicitement les collections
        # Les valeurs manquantes dont forcées à None et ne déclenchent pas d'exception
        # False par défaut
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://<username>:<password>@<atlas cluster>/<myFirstDatabase>?retryWrites=true&w=majority'
            'port': port_number,
            'username': 'db-username',
            'password': 'password',
            'authSource': 'db-name',
            'authMechanism': 'SCRAM-SHA-1'
        },
        'LOGGING': {
            'version': 1,
            'loggers': {
                'djongo': {
                    'level': 'DEBUG',
                    'propagate': False,                        
                }
            },
        }
    }
]
```


## Propriétés particulières

Les bases de données orientées document ne créent pas de liaison entre les collections. Il n'existe donc pas de cléf étrangère. 
En revhanche, un spécificité est qu'une propriété poeut être une liste ou un document (imbriqué).
Django sait gérer cela par défaut :

1. Cas de listes
```python
class Blog(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

class Entry(models.Model):
    blog = models.EmbeddedField(
        model_container=Blog
    )    
    headline = models.CharField(max_length=255)    

e = Entry()
e.blog = {
    'name': 'Djongo'
}
e.headline = 'The Django MongoDB connector'
e.save()
```

2. Cas de document imbriqué
```python
from djongo import models

class Entry(models.Model):
    blog = models.ArrayField(
        model_container=Blog
    )    
    headline = models.CharField(max_length=255)    

e = Entry()
e.blog = [
    {'name': 'Djongo'}, {'name': 'Django'}, {'name': 'MongoDB'}
]
e.headline = 'Djongo is the best Django and MongoDB connector'
e.save()
```

### Exemple de « relation » ManyToMany avec un ArrayField

```python
from djongo import models

class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    class Meta:
        abstract = True

class MetaData(models.Model):
    pub_date = models.DateField()
    mod_date = models.DateField()
    n_pingbacks = models.IntegerField()
    rating = models.IntegerField()

    class Meta:
        abstract = True

class Author(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()

    class Meta:
        abstract = True
        
    def __str__(self):
        return self.name

class Entry(models.Model):
    blog = models.EmbeddedField(
        model_container=Blog,
    )
    meta_data = models.EmbeddedField(
        model_container=MetaData,
    )

    headline = models.CharField(max_length=255)
    body_text = models.TextField()

    authors = models.ArrayField(
        model_container=Author,
    )
    n_comments = models.IntegerField()

    def __str__(self):
        return self.headline
```

