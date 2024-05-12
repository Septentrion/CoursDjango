# Interface d'administration de Django

## Introduction

Django livre d'emblée une interface d'administration des données, qui est un peu l'équivalent d'un _phpMyAdmin_ pour PHP.

## Configuration

L'interface d'administration est activée dès la création d'un projet Django. On peut le voir dans le fichier `urls.py` du dossier associé au projet (qui généralement porte le même nom que le projet).

```python
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

_A minima_, vous trouverez dans le tableau des URLs un chemain qui fait référence au paquetage d'adminsitration de Django : `admin.site.urls`.

Dans ml'exeple ci-dessus, nous avons donc unpoit d'entrée,correspondant à l'URL `<host>/admin/`, qui nous donnera accès à la gestion des données.

### Accès à l'administration

Naturellement, il faudtra aumoins un utilisateur pour pouvoir se connecter à cette interface.

C'est pourquoi, une des premières opérations à réaliser est la création d'un « *super-afministrateur* », par le biais de la commande :

```bash
./manage.py creatsuperuser
```

## Intégration des modèles

L'interface d'administration est dédiée à la gestion des données.

Au départ, ne figurent que les modèles natifs de Django, qui ont trait à la gestion des utilisateurs. Vous trouverez donc des menus :

- Users

- Groups

> Les utilisateurs sont abordés dans le chapitre 6

Nous allons progressivement créer nos propres modèles.

Par e"xemple, dans la bibliothèque, nous aurons des livres et un modèle `Book`, défini ainsi :

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

Intéger ce modèle dans l'interface d'administration nécessite de le déclarer à Django..

Nous devons référencer notre modèle auprès de Django. Pour cela, nous supposons que le modèle `Book` a été créé dans une _application_  `library`.

Dans cette application, nous devons créer un fichier `admin.py`,  qui, par défaut, se présentera ainsi :

```python
# library/admin.py

from django.contrib import admin
from library.models import Book

class BookAdmin(admin.ModelAdmin):
    pass

admin.site.register(Book, BookAdmin)
```

Nous voyons que :

- Est déclarée une classe `BookAdmin` qui, par défaut est vide.

- Sont enregistrés (`register`) les deux classes `Book` et `BookAdmin` auprès de l'administration de Django

### Personnalisation de l'administration

La classe `BookAdmin` sert en fait à personnaliser l'interface d'administration pour ce modèle particulier.

#### La vue en liste

Première étape, vous pouvez choisir quels propriétés du modèle afficher sur la vue en liste. Nous avons pour cela une option `list_display`.

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language")
```

`list_display` accepte un tuple des propriétés sélectionnées

Les colonnes peuvent être ordonnées via les _méta-options_ de la classe :

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language")

    class Meta:
        ordering = ("title", "language", "genre")
```

De surcroît, les colonnes ne sont pas **nécessairement** des propriétés du modèle. Elles peuvent correzspondre à des méthodes de la classe d'administration.

Admettons que nous voulions afficher le nombre de fois où un livre a été emprunté, nous pourrons définir une méthode `borrowing_count` et l'ajouter dans bnotre tuple.

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language", "borrowing_count")

    def borrowing_count(self, book):
        from django.db.models import Count
        result = Borrow.objects.filter(book=book).aggregate(Count("borrow"))
        return result['grade___count']

    class Meta:
        ordering = ("title", "language", "genre", "borrowing_count")
```

#### Filtrer les données par facette

Vous pouvez ajouter à l'interface une barre latérale qui permettra de filter les données en fonction des valeurs des colonnes.

Nourrions vouloir cette fonctionnalité sur les langues et les genres. Nous allons donc ajouter une otion `list_filter`.

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language", "borrowing_count")
    list_filter = ("genre", "language")

    def borrowing_count(self, book):
        from django.db.models import Count
        result = Borrow.objects.filter(book=book).aggregate(Count("borrow"))
        return result['grade___count']

    class Meta:
        ordering = ("title", "language", "genre", "borrowing_count")
```

#### Champs de recherche

Nous pouvons également paramétrer le champ de recherche avec l'option `search_fields`.

La particularité de `search_fields` est qu'elle admet des opérateurs de l'ORM de Django. Exemple :

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language", "borrowing_count")
    list_filter = ("genre", "language")
    search_fields = ("title__contains", "genre__startswith", "language__iexact")

    def borrowing_count(self, book):
        from django.db.models import Count
        result = Borrow.objects.filter(book=book).aggregate(Count("borrow"))
        return result['grade___count']

    class Meta:
        ordering = ("title", "language", "genre", "borrowing_count")
```

Le moteur de recherce nous permet de chercher :

- les titres qui contiennent une certaine chaîne de caractères

- les genres qui commencent par une certaine racine ('R', 'Es', etc.)

- les langues de amnière exacte, insesnsiblement à la casse

#### Les formulaires

Nous pouvons également personnaliser les formulaires d'édition avec les options `fields` et `fieldsets`.

- `fields`énumère la liste des champs du formulaire

- `fieldsets`, en prime, les groupe par blocs.

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language", "borrowing_count")
    list_filter = ("genre", "language")
    search_fields = ("title__contains", "genre__startswith", "language__iexact")
    fieldsets = (
        # La première valeur est le titre du bloc, affiché dans l'interface
        (None, {"fields": {"title", "abstract")}),
        ("Complément", {"fields": ("genre", "language", "publication_date")})    
    )

    def borrowing_count(self, book):
        from django.db.models import Count
        result = Borrow.objects.filter(book=book).aggregate(Count("borrow"))
        return result['grade___count']

    class Meta:
        ordering = ("title", "language", "genre", "borrowing_count")
```

De plus, nous disposons d'une méthode `get_form` pour personnaliser le formulaire lui-même et nous pouvons ajouter des contraintes de validation pour les chams-ps.

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "language", "borrowing_count")
    list_filter = ("genre", "language")
    search_fields = ("title__contains", "genre__startswith", "language__iexact")
    fieldsets = (
        # La première valeur est le titre du bloc, affiché dans l'interface
        (None, {"fields": {"title", "abstract")}),
        ("Complément", {"fields": ("genre", "language", "publication_date")})    
    )

    def borrowing_count(self, book):
        from django.db.models import Count
        result = Borrow.objects.filter(book=book).aggregate(Count("borrow"))
        return result['grade___count']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["title"].label = "Titre du livre"
        return form

    def clean_language(self):
        if len(self.cleaned_data['language']) != 2 :
            raise FormValidatinError("Les codes de langue sont sur deux caractères")    

    class Meta:
        ordering = ("title", "language", "genre", "borrowing_count")
```

#### Changer la mise en page

Enfin, nous pouvons complètement changer la mise en page de l'interface.
Celle-ci est basée sur le modèle de mise en page de Django, ce qui la rend (relativement) simple à modifier. Même si cela reste un travail long et fastidieux.

Pour faire votre prore interface, vous devrez :

1. Créer votre propre arborescence de fichiers, compatible avec ce qu'attend Django, en parrticvulier deux sous-dossiers `admin` et `registration`
2. Mdofoer la configuration de la variable `TEMPLATES` dans le fichier `settingsz.py `., pour y ajouter la racine de cette arborescence.

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # Si les gabarits sont créés dans le dossiers "/templates"
            # à la racine du projet
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

## Ressources

- [Documentation officielle](https://docs.djangoproject.com/fr/5.0/ref/contrib/admin/)
- [RealPython sur l'administrartion](https://realpython.com/customize-django-admin-python/#overriding-django-admin-templates)
- [Tutoriel sur la personnalisation de l'administratrion](https://testdriven.io/blog/customize-django-admin/)
