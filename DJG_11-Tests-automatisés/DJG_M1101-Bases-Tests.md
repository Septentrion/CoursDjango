# Les tests automatisés pour Django

## Introduction

La question de tests automatisés cdouvre un très large spectre, et il est quelquefois difficile de catégoriser les différents types de test. On peut toutefois distinguer trois grandes familles de tests :

- les **test unitaires**, qui visent à s'assurer de la sémantique de chque fonction isolée de sont contexte, autrement dit qu'un fonction, supposée pure, correspond bien à ce que l'on en attend ;

- les **tests fonctionnels** ou **tests d'intégration**, qui permettent de valider, grosso modo, des procédures engageant une série de fonctions — on s'attache ici plutôt aux dépendances ;

- les **tests de bout en bout** (quelqufois appelés **E2E**), qui mettent en œuvre des scénarios utilsateurs complexes, comprenant, dans le cas du web, des fonctionnalités du client lui-même, indépendamment du serveur.

Par ailleurs, naturellement, il existe beaucoup d'autres catégories ou sous-catégories de tests, comme :

> ... la boîte noire, la boîte blanche, les tests manuels, automatiques, de canari (canary), de fumée (smoke), de conformité (conformance), d'approbation (acceptance), fonctionnels, système, performance, chargement et stress. ...
> 
> — MDN —

## L'infrastructure de tests de Django

Django intègre un environnement de tests basé sur la bibliothèque standard de Python `unittest`, et plus pcésément de la classe `unittest.TestCase`.

Django définit sa propre hiérarchie de classes de tests que l'on peut représenter ainsi :

![Classes de tests de Django](/Users/ferdydurke/Documents/Projets/Formation/Cours/Django/DJG_11-Tests-automatisés/images/django_unittest_classes_hierarchy.svg)

La classe de test la plus souvent utilisée est `TestCase`, car permet de prendre enb coimpte la plupart des aspects des applications. `SimpleTestCase, par exemple, ne permet de tester les requêtes vers les bases de données.

Ce qui manque à `TestCase`, c'est la possibilité des tester des scénatios utilisateur incluant uncient web. Dans ce cas-là, on utilisera `LiveServerTextCase`, dont c'est le rôle. Cette classe permet d'interagir avec des simulateurs tels que  **Selenium**.

### Organisation des classes de test

Grâce aux possibilités de `unittest`, Django peut découvrir automatiquement nos procédures. Nous sommes donc libres d'organiser les dossiers et les fichiers comme nous le souhaitons.

Généralement, on créera dans chaque applilcation un dossier `/tests`, à l'intérieur duquel nous implémenterons nos prcocédures. Poiur être repéré, ce dossier doit être un *package*  et doit donc comporter un fichier `__init__.py`.

La seule contrainte que nos devons repecter, par défaut, est de  nommer les fichiers et les fonctions tel qu'attendu par `unittest`, c'est-à-dire :

```regex
/test(_[\w_]+)?/
```

*(avec l'extention `.py` pour les fichiers)*

## Premiers tests

Une classe de tests typique se présente de la manière suivante :

```python
# <chemin>/tests/test_a.py

# Import de la classe de test de base
from django.test import TestCase


class YourTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Configuration effectuée une fois pour chaque classe de tests
        """
         pass

    def setUp(self):
        """
        Configuration effectuée avant chaque test
        """
        pass

    def test_false_is_false(self):
        """
        Teste False 
        """
        self.assertFalse(False)

    def test_false_is_true(self):
        """
        Teste True 
        """
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        """
        Teste une opération arithmétique 
        """
        self.assertEqual(1 + 1, 2)
```

### Lancement des tests

Une fois nos premiers tests écrtits, nous n'avons plus qu'à lancer les procédures avec la commande :

```bash
./manage.py test <chemin>.test.test_a.test_one_plus_one_equals_two
```

Entre autres optins, la commande permete de régler la granularité des test jusqu'au niveau des fonctions indivuelles. nous pourrons donc exécuter,  en nous référant au modèle ci-dessus :

```bash
./manage.py test <chemin>.test.test_a.test_one_plus_one_equals_two 
```

### Tester un modèle

Le modèles sont souvent les classes les plus implesà tester puisqu'elles ne sont que des moyens de faire le lien entre le modèle objet et le modèle de la base de données. Néanmoins, comme nous l'avons vu, nous pouvons ajouter au modèle autant de propriétés virtuelles que nous le souhaitons. Et celles-ci peuvent transformer de manière arbitraire les données initiales.

Prenons un modèle de livre :

```python
# /library/models.py

from datetime import datetime
from django import models

class Book(models.Model):
    title = models.CharField()
    abstract = models.TextField()
    acquisition_date = models.DateField()
    category = models.ForeignKey(Category)

    @property
    def age():
        """
        Nombre d'années écoulées depuis l'acquisition
        """
        return round(((datetime.today() - self.acquisition_date()).days)/365))
```

```
La classe de base `TestCase` nous permet de dialoguer avec la base de données. Par exemple :

```python
# /library/test/test_models.py

from datetime import datetime
from django.test import TestCase
from library.models import Book

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Book.objects.create(title='Ulysse', acquisition_date=datetime(2012,05,20)

    def test_age(self):
        book = Book.objects.get(id=1)
        self.assertEquals(book.age, 12)
```

### Test un formulaire

Que tester dans un formulaire ?

Globalement, nous pouvons vouloir nous assurerr :

1. Que le fromulaire s'affiche comme nous le voulons

2. Que nos procédures de validation fonctionnent correctement

Nous vpourrions aussi vouloir créer nos prores champs de formulaires, qu'il faudrait alors tester plus en détail, mais nous n'aborderons pas le sujet ici.

Comme nous n'utilisons pas la base de données dans ce cas, nous pouvons partir de la classe `SimpleTestCase`, qui suffira à nos besoins.

Voici un fomrulaire pour renouveler un emprunt, dans une limite de 4 semaines.

```python
class RenewBookForm(forms.Form):
    """
    Renouvellement d'emprunt, au maximum de 4 semaines.    
    """
    renewal_date = forms.DateField(help_text="Entrez une date (max. 4 semaines)")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # La date ne doit pas .
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check if date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data
```

La classe de tests correspondante :

```python
import datetime

from django.test import SimpleTestCase
from django.utils import timezone

from catalog.forms import RenewBookForm

class RenewBookFormTest(TestCase):
    def test_renew_form_date_field_label(self):
        form = RenewBookForm()
        self.assertTrue(form.fields['renewal_date'].label == None or form.fields['renewal_date'].label == 'renewal date')

    def test_renew_form_date_field_help_text(self):
        form = RenewBookForm()
        self.assertEqual(form.fields['renewal_date'].help_text, 'Enter a date between now and 4 weeks (default 3).')

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewBookForm(data={'renewal_date': date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertTrue(form.is_valid())
```

## Ressources

- [unittest — Découverte automatique des classes de test](https://docs.python.org/3/library/unittest.html#unittest-test-discovery)
