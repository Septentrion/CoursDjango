# Les  formulaires

## Introduction

## Implémentation

### Écriture d’un formulaire minimal¶

Nous voulons maintenant créer un formulaire qui permette à une personne d'ajouter un livre dans notre biblothèque. Dans un premier temps, nous définissons un formulaire très simple qui comprendra un titre des des mots-clefs, ainsi que la date de l'ajout (qui pourrait être ajoutée automatiquement, bien entendu).

Pour cela, si nous étions dans un site écrit en Python natif, nous devrions créer une structure HTML qui ressemblerait à ceci (*a minima*) :

```html
library/templates/library/form_add.html¶
<form action="{% url 'library:add' %}" method="post">
{% csrf_token %}
<fieldset>
    <legend>Ajouter un livre</legend>
    {% if error_message %}<p><strong>{{ error_message }}</strong></p>{% endif %}
    <input type="text" id="title" name="title" />
    {% for keyword in keywords.all %}
        <input type="checkbox" name="keywords" id="key-{{ forloop.counter }}" value="{{ keyword.id }}">
        <label for="key-{{ forloop.counter }}">{{ keyword.label }}</label><br>
    {% endfor %}
    <input type="date" id="insertion-date", name="insertion-date" />
</fieldset>
<input type="submit" value="Ajouter">
</form>
```

Ce formulaire contient :

- un champ textuel pour le titre de l'ouvrage
- une liste de cases à cocher pour attribuer des mots-clefs à cet ouvrave
- un jeton de sécurité, par l'intermédiaire de l'instruction `{% csrf_token %}` qui permet à Django de vérifier la provenance du formulaire qu'il recevra en retour. Cela évitera les attaques des type CSRF (Cross-Site Request Forgery)
- un URL de retour `{% url 'library:add' %}` contenant le nom de la route à suivre, préfixée par `library` car nous avons défini une variablme `app_name` dans le fichier `views.py`
- un compteur arbitraire `forloop.counter`, qui nous permet de générer des id uniques pour les champs du formulaire.

### Les classes de formulaires

Toutefois, si nous utilisons Django, nous n'aurons pas (et nous ne devrons pas, en général) créer les formulaires directement en HTML.
Nous passerons par des **classes de formulaires**.
Celles-ci sont des sous-classes de la classe générique `Form`.

La syntaxe de déclaration pour un `Form` est très semblable à celle utilisée pour déclarer un `Model` — ces classes partagent les mêmes types de champs (et des paramètres similaires). Ceci est logique puisque, dans les deux cas, nous avons besoin de nous assurer que chaque champ gère le bon type de données, se limite aux données valides, et a une description pour l'affichage/la documentation.

La casse qui nous permet d'ajouter un livre pourrait ressembler à ceci :

```python
# form_add.py

from django import forms

class AddBookForm(forms.Form):
  insertion_date = forms.DateField()
  title = forms.CharField()
  keywords = forms.MultipleChoiceField()
```

#### Attributs des champs de formulaire

Dans l'exemple ci-dessus, nous avons laissé les types de chmaps « _nus_ ». 
Chacun peut néanmoins être paramétré à l'aide d'une série d'options :

|                    |                                                                                                                                                                                                                                                                            |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **required**       | Si True, le champ ne peut être laissé vide ou recevoir une valeur None. Les champs sont requis par défaut, aussi devez-vous préciser required=False pour autoriser des valeurs vides dans le formulaire.                                                                   |
| **label**          | Le label à utiliser au moment de rendre le champ en HTML. Si label n'est pas précisé, alors Django en créera un à partir du nom du champ concerné, en mettant en majuscule la première lettre et en remplaçant les tirets bas par des espaces (par exemple, Renewal date). |
| **label_suffix**   | Par défaut, un double point est affiché après le label (par exemple, Renewal date​:). Cet argument vous permet de préciser un suffixe différent contenant un ou plusieurs autres caractère(s).                                                                             |
| **initial**        | La valeur intiale pour le champ lorsque le formulaire est affiché.                                                                                                                                                                                                         |
| **widget-**        | Le widget d'affichage à utiliser.                                                                                                                                                                                                                                          |
| **help_text**      | Un texte supplémentaire qui peut être affiché dans les formulaires pour expliquer comment utiliser le champ.                                                                                                                                                               |
| **error_messages** | Une liste des messages d'erreur pour le champ. Vous pouvez remplacer les messages par défaut par vos propres messages si besoin.                                                                                                                                           |
| **validators**     | Une liste de fonctions qui seront appelées quand le champ sera validé.                                                                                                                                                                                                     |
| **localize**       | Autorise la forme locale des données de formulaire (voir le lien pour plus d'informations).                                                                                                                                                                                |
| **disabled**       | Si True, le champ est affiché, mais sa valeur ne peut être modifiée. False par défaut.                                                                                                                                                                                     |

```python
# form_add.py

from django import forms

class AddBookForm(forms.Form):
  insertion_date = forms.DateField(label="Date d'ajout", required=False, help_text="Entrez la date d'ajout (facultatif)" )
  title = forms.CharField(label="Titre du livre", help_text="Donnez le titre du livre")
  keywords = forms.MultipleChoiceField(label="Mots-clefs", help_text="Attribuez des mots-clefs au livre")
```

Chaque type de champ peut également avoir des atributs qui lui sont spécifiques comme `max_length`pour les champs de types `Charfield` par exemple.

Nous avons donc maintenant un modèle de formulaire prêt à l'emploi.

### Traitement des formulaires

Maintenant, nous devons créer une vue gère le formulaire.

Naturellement, il faut une route :

```python
# library/urls.py¶
path("add/", library.add, name="book_add"),
# ...
```

Et implémenter la vue dans `views.py` :

```python
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

def renew_book_librarian(request, pk):

  # Si le livre n'existe pas, alors cela produit une erreur 404.
  # L'exception est gérée par la fonction `get_object_or_404`
  book_instance = get_object_or_404(BookInstance, pk=pk)

  # S'il s'agit d'une requête POST, traiter les données du formulaire.
  if request.method == 'POST':

    # Créer une instance de formulaire et la peupler avec des données récupérées dans la requête (liaison) :
    form = AddBookForm(request.POST)

    # Vérifier que le formulaire est valide :
    if form.is_valid():
      # Traiter les données dans form.cleaned_data tel que requis (ici on les écrit dans le champ de modèle due_back) :
      book_instance.due_back = form.cleaned_data['insertion_date']
      # Les données sont enregistrées via l'ORM de Django
      book_instance.save()

      # Rediriger vers une nouvelle URL :
      return HttpResponseRedirect(reverse('all-borrowed'))

  # S'il s'agit d'une requête GET (ou toute autre méthode), créer le formulaire par défaut.
  else:
    proposed_date = datetime.date.today()
    form = AddBookForm(initial={'insertion-date': proposed_date})

  context = {
    'form': form,
    'book_instance': book_instance,
  }

  return render(request, 'catalog/book_renew_librarian.html', context)
```

> ![WARNING]
> Attention : Alors que vous pouvez accéder aussi aux données de formulaire directement à travers la requête (par exemple, request.POST['renewal_date'], ou request.GET['renewal_date'] si vous utilisez une requête GET), ce n'est PAS recommandé. Les données nettoyées sont assainies, validées et converties en types standard Python.

### Affichage des formulaires

Django sait afficher simplement les formulaires. Il suffit de les déclarer comme des variables **Jinja**, en précisant que nous les voulons en tableau. La variable `form` a été construite dans la vue, comme nous pouvons le voir juste au-dessus.

```jinja
{% extends "base.html" %}

{% block content %}
  <h1>Ajouter: {{ book_instance.book.title }}</h1>

  <form action="" method="post">
    {% csrf_token %}
    <table>
    {{ form.as_table }}
    </table>
    <input type="submit" value="Ajouter">
  </form>
{% endblock %}
```

> [!WARNING]
> Remarquez que le jeton de sécurité CSRF n'est pas ajouté automatiquement par Django. Ne l'oubliez poas !

#### Affichage de granularité fine

Il est possible de créer une mise en page beaucoup plus personnelle, en déclarant séparément les champs. Chacun à quatre attributs :

|                                        |                           |
| -------------------------------------- | ------------------------- |
| `{{ form.renewal_date }}`              | Le champ complet.         |
| `{{ form.renewal_date.errors }}`       | La liste des erreurs.     |
| `{{ form.renewal_date.id_for_label }}` | L'id du label.            |
| `{{ form.renewal_date.help_text }}`    | Le texte d'aide du champ. |

Nous pouvons maintenant expérimenter le formulaire.

## Variante d'après les modèles

Il est possible de créer les classes de formulaires en se basant sur les modèles correspondant. En effet, comme nous l'avons vu plus haut, les types de champs sont les mêmes dans les deux cas.

### Surcharge de la classe ModelForm

La principale différence tien au fait que ces classes de formulaies héritent de `ModelForm` et non de `Form`. Ceci permet de simmlfier leur définition. Par exemple, admettons que nous ayons une classe `Author` :

```python
class Author(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=3, choices=TITLE_CHOICES)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
```

La classe de formulaire correspondante s'écrira poar défaut :

```python
class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ["name", "title", "birth_date"]
```

Si l'on a besoin de préciser des informations sur le formulaire :

```python
from django.utils.translation import gettext_lazy as _


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ["name", "title", "birth_date"]
        labels = {
            "name": _("Writer"),
        }
        help_texts = {
            "name": _("Some useful help text."),
        }
        error_messages = {
            "name": {
                "max_length": _("This writer's name is too long."),
            },
        }
```

### Utilisation de « factories »

Il est aussi possible de créer des formulaires dynamiquement en utilisant une « factory ». Pour un `Author`, nous pourions écrire :

```python
from django.forms import modelform_factory
>>> from myapp.models import Author
>>> AuthorForm = modelform_factory(Author, fields=["name", "title"])
```

## Hydratation des formulaires

Dans un certain nombre de cas, nous aurons besoin de formulaires pré-remplis (en cas de modification, par exemple).
Si nous avons besoin de lier un formulaire à un objet particulier, il suffit de passer celui-ci au constructeur, sous forme de dictionnaire :

```python
author = {name: "Victor Hugo", title: "M."}
form = AuthorForm(author)
```

La classe de formulaire possède un attribut `is_bound` qui indique si des données sont liées ou non au formulaire.

`Form` admet aussi un attribut `initial_data` qui peut servir dans deux situations :

1. Si le formulaire n'est pas lié, nous pourrons passer des vaelurs initiales à certains champs du formulaire.
2. Si le formulaire est lié, nous pouvons nous en servir poure détecter quels sont les champs qui ont été modfifiés, grâce à la méthode `has_changed`.

```python
data = {
    "subject": "hello",
    "message": "Hi there",
    "sender": "foo@example.com",
    "cc_myself": True,
}
modified = data.copy()
modified["subject"] = "Welcome"

f = ContactForm(modified, initial=data)

# --> True
f.has_changed()

# --> ["subject"]
f.changed_data
```

## Ressources

- [Documentation officielle sur les formulaires](https://docs.djangoproject.com/fr/5.0/topics/forms/)
- [Formulaires créés d'après les modèles](https://docs.djangoproject.com/fr/5.0/topics/forms/modelforms/)
- [Référence des champs de formulaire](https://docs.djangoproject.com/fr/5.0/ref/forms/fields/)
- [L'API de formulaire](https://docs.djangoproject.com/fr/5.0/ref/forms/api/#ref-forms-api-bound-unbound)
