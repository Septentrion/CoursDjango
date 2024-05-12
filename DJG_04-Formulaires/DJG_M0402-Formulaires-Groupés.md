# Formulaires groupés

## Introduction

Les modèles de dopnnées comportent souvent des liaisons, en particulier lles modèles relationnels.

Nous pouvons alors nous trouveer dans deux cas de figures :

1. Nous souhaitons lier un objet « enfant » à un objet « parent »
2. Nous voulons lier un objet « parent » à une collection d'objets « enfants »

## Implémentation

### D'enfant à parent

Si notre modèle définit des clefs étrangères, nous aurons vraisemblablement besoin de lier les deux lorsque nous remplirons un formulaire.

Heureusmeent, Django nous fournit un type de chmaps spécifique : `ModelChoiceField`.

> [!NOTE]
> Ceci est vrai pour les modèles relationnels. Dans le cas où nous utiliserions une base de données orienté document, comme MongoDB, il existe d'autes types de champs spécifiques :
> 
> - `EmbeddedField`
> - `ListField`

Consiédrons un modèle de livre `Book` lié à un auteur : 

```python
class Author(models.Model:
    first_name=models.CharField(max_length=128)
    last_name=models.CharField(max_length=128)

class Book(models.Model):
    title=models.CharField(max_length=128)
    author=models.ForeignKey(Author)
    publication_date=models.DateTime()
```

La liaison est indiquée par le type de champ `ForeignKey`.

Le formulaire correspondant s'écrit ainsi:

```python
class BookForm(forms.Form):
    title = forms.CharField(max_length=128, help_text="Entrez le titre du livre.")
    author = forms.ModelChoiceField(query_set=Author.objects.all(), help_text="Choisissez un auteur.")
```

Le champ `ModelChoiceField` admet un paramètre (nommé) `query_set` qui lui associe un jeu de données.

La classe `Author` devrait alors probablement implémenter la méthode magique `__str__` afin d'afficher jne chaîne de caractères dans le formulaire.

#### Variante

Il devrait âtre également possible d'utiliser simplement un champ `ChoiceField` de cette manière :

```python

```

### De parent à enfant

Nous pouvons également faire l'inverse.

Prenons l'exemple précédent et admettons que nous vouions créer une fiche Auteur, accompagnée d'une liste de livres qu'il a écrits. Dans ce cas, nous aurons plutôt intérêt à créer le formulaire dynamiquement comme `FormSet` :

```python
# forms.py

from django.forms.models import inlineformset_factory

# Une variable pour rendre le nombre de sous-formulaires paramétrable
opus = 5
BooksFormSet = inlineformset_factory(models.Author, models.Book, extra=opus)
```

Il faut ensuite écrire la vue correspondante :

```python
# views.py
from forms import BooksFormSet

def collect_books(request, author_id, opus):
    """Edit children and their addresses for a single parent."""

    author = get_object_or_404(models.Author, id=author_id)

    if request.method == 'POST':
        formset = BooksFormSet(request.POST, instance=author)
        if formset.is_valid():
            formset.save()
            return redirect('author_view', author_id=author.id)
    else:
        formset = BooksFormSet(instance=author)

    return render(request, 'collect_books.html', {
                  'parent':author,
                  'children_formset':formset})
```

Nous aurons enfin besoin  d'un gabarit d'affichage :

```python
# collect_books.html

{{ children_formset.management_form }}
{{ children_formset.non_form_errors }}

{% for child_form in children_formset.forms %}
    {{ child_form }}

{% endfor %}
```
