# Créer ses propres utilisateurs

## Introduction

## Création d'une application pour les utilisateurs

Le principe général est de créer une application spécifique pour la gestion des utlilsateurs.

> [!NOTE]
> 
> Rappelons que ce que Django appelle une « *application* » est plutôt ce que Symfony appelle un « *bundle* » (un paquetage), c'est-à-dire une unité fonctionnelle cohérente et (relativement) autonome

```bash
./manage.py startapp users
```

Naturellement, nous ne devons pas oublier de déclarer cette application dans le fichier `settings.py`.

```python
# settings.py

INSTALLED_APPS = [
    "users",
    # ... Autres applications
]
```

### Création du modèle

L'application `users` n'a rien de particulier. Elle va nous servir à créer notre propre modèle d'utilisateur. Pour cela nous avons encore trois possibilités.

#### Utiliser un modèle mandataire

Dans certains cas, nous ne souhaitons pas modifier la structure du modèle, mas simplement son comportement (ajouter des méthodes, surcharger les attributs `Meta`, etc.).

Nous pouvons alors utiliser un _modèle proxy_ .

```python
# users/models.py

from django.contrib.auth.models import User

class Gamer(User):
    class Meta:
        proxy = True

    def do_something(self):
        pass
```

Notre classe `Gamer` est maintenant un équivalent de `User` :

```python
p = User.objects.create_user("john", "lennon@thebeatles.com", "lucy")
g = Gamer.objects.get(first_name="foobar")
```

### Etendre le modèle User

Nous pouvons éventuellement ajouter des propriétés nouvelles la classe. Dans ce cas, il faudrait ajouter une association `OneToOne` à celle-ci pour « hériter » des caractéristiques de User. Par exemple :

```python
from django.contrib.auth.models import User

class Gamer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField()
```

Cela crée une indirection qui rend le modèle moins uniforme :

```python
john = User.objects.get(username="john")
print(john.gamer.level
```

### Créer un nouveau modèle d'utilisateur

La solution la plus uniforme est de créer sa (ou ses) propre(s) classes d'utilisateur(s). Dans ce cas, le processus et un peu plus complexe.

#### Création du modèle

La première étape est de définir le modèle de référénce. Celui-ci doit hériter de `AbstractUser`.

```python
# users/models.py

from django.contrib.auth.models import AbstractUser

class LibrayrUser(AbstractUser):
    pass
```

Premièrement, nous pouvons annuler toutes les propriétés du mocèle parent dont nous n'avons pas besoin. A titre d'exemple, nous n'avons pas besoin de `username` car l'identifant est l'adresse électronique de la personne :

```python
# users/models.py

from django.contrib.auth.models import AbstractUser

class LibrayrUser(AbstractUser):
 # la propriété `username` est supprimée du modèle
 username = None

 # Mais comme celle-ci était la clef primaire, il faut la redéfinir :
 # - Ajout d'e l'adresse électronique
 email = models.EmailField("email address", unique=True)

 # L'identifiant de l'utilisateur est son adresse électronique
 USERNAME_FIELD = "email"
```

Deuxièmement, nous pouvons maintennt ajouter toutes les propriétés nouvelles dont nous avons besoin.

```python
class LibrayrUser(AbstractUser):
 # ...
 date_of_birth = models.DateField(
    verbose_name="Anniversaire",
    null=True
 )
 city_of_residence = models.charField(
     verbose_name="Ville de résidence",
     max_length=100
```

Nous pouvons ensuite définir des propriétés comme obligatoires ;

```python
class LibrayrUser(AbstractUser):
 # ...
 REQUIRED_FIELDS = [
     first_name, last_name, date_of_birth, city_of_residence
 ]
```

Et, **très important**, nous devons surcharger la valeur de la propriété `objects`, qui permet la communication entre le modèle et la base de données. Cette classe va ^étre défnie juste après.

```python
class LibrayrUser(AbstractUser):
 # ...
 objects = LibraryUserManager()
```

Il est également possible d'ajouter toutes les méthodes utiles... dont la méthode magique `__str__`.

#### Le gestionnaire de modèle

Il nous faut donc aussi une classe pour gérer la communication avec la base de données. Cette classe doit hériter de `BaseUserManager`.

- [Code source de BaseUSerManager](https://github.com/django/django/blob/main/django/contrib/auth/base_user.py)

```python
from django.contrib.auth.base_user import BaseUserManager

class LibraryUserManager(BaseUserManager)
    pass
```

Cette doit nous servir en particulier à redéfinir comment créer un utilisateur (`create_user`) :

```python
def create_user(self, email, password, date_of_birth, **extra_fields):
    # Si le mail n'est pas défini, déclencher une erreur
    if not email:
        raise ValueError(_("The Email must be set"))

    # Le mail est normalsé (mis en minuscules)
    email = self.normalize_email(email)

    # Création de l'objet `CustomUser`
    user = self.model(
        date_of_birth=date_of_birth,
        email=email,
        **extra_fields
    )

    # Hachage du mot de passe
    user.set_password(password) # hash raw password and set

    # Enregistrement deans la base de données
    user.save()

    return user
```

... et comment créer un super-utilisateur (create_superuser) :

```python
def create_superuser(self, email, password, date_of_birth, **extra_fields):
    # Fait du groupe 'staff'
    extra_fields.setdefault("is_staff", True)
    # Est une super-utilisateur
    extra_fields.setdefault("is_superuser", True)
    # Le nouvel utilisateur est actif
    extra_fields.setdefault("is_active", True)

    if extra_fields.get("is_staff") is not True:
        raise ValueError(
            _("Superuser must have is_staff=True.")
        )
    if extra_fields.get("is_superuser") is not True:
        raise ValueError(
            _("Superuser must have is_superuser=True.")
        )
    return self.create_user(
        email,
        password,
        date_of_birth,
        **extra_fields
    )
```

#### Intégration dans l'interface d'adminitration

Comme nous avons un noveau modèle, nous pouvons choisir comment il doit se présenter dans l'interface d'administration du projet.

Pour cela, nous allons modifier le fichier `admin.py` pour créer une classe ad hoc. Celle-ci est en fait très simple et déclarative. Voici un exemple :

```python
# users/admin.py

class LibraryUserAdmin(UserAdmin):
    # Modèle de référence
    model = LibraryUser

    # Liste de propriétés du modèle à afficher
    list_display = (
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "city_of_residence",
        "is_staff",
        "is_active",
        "is_superuser",
    )

    # olonnes filtrables
    list_filter = (
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "is_staff",
        "is_active",
        "is_superuser",
    )

    # Groupes de champs pour le formulaire
    fieldsets = (
        (None, {"fields": (
            "first_name",
            "last_name",
            "email",
            "password",
            "date_of_birth")}
        ),
        ("Permissions", {"fields": (
            "is_staff",
            "is_active",
            "groups",
            "user_permissions")}
        ),
    )

    # GRoupes de champs pour la création
    add_fieldsets = (
        ( None, {"fields": (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "date_of_birth",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions")}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)```
```

#### Configuration du projet

Pour terminer il ne faut pas oublier :

1. D'enregister le modèle dans l'interface d'administration :

```python
#users/admin.py

# Inclusion de User dans l'interface d'administration
admin.site.register(LibraryUser, LibraryUserAdmin)
```

2. De définir notre classe d'utlisateur comme référence pour le projet :

```python
# project/settings.py

AUTH_USER_MODEL = "users.LibraryUser"
```

3. Faire la migration

```bash
python manage.py makemigrations
python manage.py migrate
```
