# Validation de formulaires et de champs¶

## Introduction

La validation de formulaire intervient lorsque les données sont nettoyées. Si vous souhaitez personnaliser ce processus, Trois types de méthodes de nettoyage sont exécutés durant le traitement d’un formulaire. Elles sont normalement exécutées lorsque la méthode `is_valid()` d’un formulaire est appelée. 

En général, toute méthode de nettoyage peut générer l’exception `ValidationError` si un problème survient lors du traitement des valeurs, en passant des informations adéquates au constructeur de `ValidationError`.

La majeure partie de la validation peut se faire à l’aide de **validateurs**, des fonctions utilitaires pouvant être réutilisées. Il s’agit de fonctions (ou objets exécutables) acceptant un seul paramètre et générant une exception `ValidationError` en cas de saisie non valide. Les validateurs sont exécutés après l’appel aux méthodes `to_python` et `validate` du champ.

La validation d’un formulaire est partagée en plusieurs étapes, qui peuvent être personnalisées ou surchargées :

1. La méthode `to_python()` d’un champ `Field` est la première étape de toute validation. Elle transforme la valeur dans le bon type de données et génère ValidationError si ce n’est pas possible. Cette méthode accepte la valeur brute provenant du composant et renvoie la valeur convertie. Par exemple, un champ FloatField transforme la donnée en un objet Python float ou génère une exception ValidationError.

2. La méthode `validate()` d’un champ `Field` se charge de la validation spécifique du champ qui ne convient pas pour un validateur. Elle accepte une valeur ayant déjà été convertie dans le bon type et génère une exception ValidationError en cas d’erreur. Cette méthode ne renvoie rien et ne doit pas modifier la valeur. Elle peut être surchargée pour gérer de la logique de validation que vous ne pouvez ou ne voulez pas placer dans un validateur.

3. La méthode `run_validators()` d’un champ lance tous les validateurs du champ et rassemble toutes les erreurs dans une seule exception ValidationError. Il n’est en principe pas utile de surcharger cette méthode.

4. La méthode `clean()` d’une sous-classe de champ est responsable de l’exécution de `to_python()`, `validate()` et `run_validators()` dans le bon ordre et de la propagation des erreurs. Si à tout moment l’une de ces méthodes génère une exception `ValidationError`, la validation s’arrête et cette erreur est propagée. Cette méthode renvoie les données nettoyées qui sont ensuite insérées dans le dictionnaire cleaned_data du formulaire.

5. La méthode `clean_<nom_du_champ>()` est appelée pour une sous-classe de formulaire – où <nom_du_champ> est remplacé par le nom de l’attribut de champ de formulaire. Cette méthode s’occupe de tout nettoyage spécifique à cet attribut, sans considération du type de champ concerné. Cette méthode ne reçoit aucun paramètre. Vous devez chercher vous-même la valeur du champ dans `self.cleaned_data` et vous rappeler qu’il s’agira à ce moment d’un objet Python, pas de la chaîne initialement soumise avec le formulaire (la valeur figure dans cleaned_data parce que la méthode générale clean() du champ aura déjà nettoyé la valeur une première fois).

Par exemple, si vous souhaitiez valider que le contenu d’un champ `CharField` nommé `serialnumber` est unique, `clean_serialnumber()` serait le bon endroit pour le faire. Vous n’avez pas besoin d’un champ spécifique (c’est un CharField), mais vous avez besoin d’une séquence de validation propre au champ de formulaire et, si possible, de nettoyer/normaliser les données.

La valeur renvoyée par cette méthode remplace la valeur existante dans `cleaned_data`, il doit donc s’agir soit de la valeur de `cleaned_data` (même si cette méthode ne l’a pas modifiée), soit d’une nouvelle valeur propre.

La méthode `clean()` de la sous-classe de formulaire peut effectuer toute validation nécessitant d’accéder à plusieurs champs de formulaire. C’est ici que vous pouvez placer des contrôles du genre : si le champ A est renseigné , le champ B doit contenir une adresse de messagerie valide. Cette méthode peut renvoyer un dictionnaire complètement différent si elle le souhaite, et ce résultat sera utilisé comme contenu de cleaned_data.

Comme les méthodes de validation des champs ont été exécutées au moment où `clean()` est appelée, vous avez aussi accès à l’attribut errors du formulaire qui contient toutes les erreurs générées lors du nettoyage individuel des champs.

Notez que toute erreur générée par votre version de Form.clean() ne sera associée à aucun champ particulier. Elles sont attribuées à un « champ » spécial nommé __all__ auquel il est possible d’accéder par la méthode non_field_errors() en cas de besoin. Si vous souhaitez lier une erreur à un champ spécifique du formulaire, vous devrez appeler add_error().

Notez également qu’il faut tenir compte de considérations particulières lors de la surcharge de la méthode `clean()` d’une sous-classe de `ModelForm.

Ces méthodes sont exécutées dans l’ordre metnionné ci-dessus, un champ après l’autre. C’est-à-dire que pour chaque champ du formulaire (dans l’ordre où ils ont été déclarés dans la définition du formulaire), la méthode Field.clean() (ou sa version surchargée) est exécutée, puis clean_<nom_du_champ>(). Finalement, après que ces deux méthodes ont été exécutées pour chaque champ, la méthode Form.clean() ou sa version surchargée est exécutée dans tous les cas, même si les méthodes précédentes ont généré des erreurs.

Des exemples pour chacune de ces méthodes sont présentés ci-dessous.

Comme mentionné, chacune de ces méthodes peut générer une exception ValidationError. Pour chaque champ, si la méthode Field.clean() gènère une erreur ValidationError, la méthode de nettoyage spécifique au champ n’est pas appelée. Cependant, les méthodes de nettoyage de tous les autres champs sont tout de même exécutées.

## La validation en pratique

Les sections précédentes ont expliqué comment fonctionne la validation de manière générale pour les formulaires. Comme il est parfois plus simple de remettre les choses à leur place en examinant du code en contexte, voici une série de petits exemples qui font usage de chacune des fonctionnalités présentées précédemment.

#### Utilisation des validateurs¶

Les champs de formulaire (et de modèle) de Django gèrent des fonctions et classes utilitaires connus sous le nom de validateurs. Un validateur est un objet exécutable acceptant une valeur et ne renvoyant rien si la valeur est valide ou générant une exception `ValidationError` si elle ne l’est pas. Ces validateurs peuvent être transmis à un constructeur de champ par l’intermédiaire du paramètre validators du champ ou définis dans une classe Field par leur attribut default_validators.

Des validateurs peuvent être employés pour valider des valeurs d’un champ ; examinons par exemple le champ SlugField de Django :

```python
from django.core import validators
from django.forms import CharField

class SlugField(CharField):
    default_validators = [validators.validate_slug]
```

Comme vous pouvez le voir, `SlugField` est un `CharField` doté d’un validateur particulier validant que le texte soumis obéit à certaines règles textuelles. Cela peut aussi se faire lors de la définition du champ, ainsi :

```python
slug = forms.SlugField()
# est équivalent à :
slug = forms.CharField(validators=[validators.validate_slug])
```

Des cas courants comme la validation d’une adresse électronique ou d’une expression régulière peuvent être traités avec des classes de validation existantes de Django. Par exemple, `validators.validate_slug` est une instance de `RegexValidator` construite avec son premier paramètre équivalent au motif `^[-a-zA-Z0-9_]+$`. Consultez la section sur l’écriture de validateurs pour voir une liste de ce qui est déjà disponible et pour des exemples de la façon d’écrire un validateur.

#### Nettoyage par défaut des champs de formulaire¶

Créons tout d’abord un champ de formulaire personnalisé qui valide que sa valeur d’entrée est une chaîne contenant des adresses électroniques séparées par des virgules. La classe complète ressemble à ceci :

```python
from django import forms
from django.core.validators import validate_email

class MultiEmailField(forms.Field):
    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(",")

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        for email in value:
            validate_email(email)
```

Pour chaque formulaire utilisant ce champ, ces méthodes seront exécutées avant que quoi que ce soit puisse être fait avec les données du champ. Il s’agit de nettoyage spécifique à ce type de champ, quelle que soit la manière dont il sera utilisé par la suite.

Créons un formulaire ContactForm pour montrer comment ce champ peut être utilisé :

```python
class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    recipients = MultiEmailField()
    cc_myself = forms.BooleanField(required=False)
```

Utilisez `MultiEmailField` comme n’importe quel autre champ. Lorsque la méthode `is_valid()` est appelée pour le formulaire, la méthode `MultiEmailField.clean()` sera aussi exécutée dans le contexte du processus de nettoyage, et celle-ci appellera à son tour les méthodes personnalisées `to_python()` et `validate()`.

#### Nettoyage d’un attribut de champ spécifique

En poursuivant l’exemple précédent, supposons que dans notre formulaire `ContactForm`, nous aimerions être certain que le champ `recipients` contienne toujours l’adresse "fred@example.com". Il s’agit de validation spécifique à notre formulaire, ce qui explique que nous ne voulions pas la placer dans la classe générique `MultiEmailField`. Au lieu de cela, nous écrivons une méthode de nettoyage qui agit sur le champ recipients, comme ceci :

```python
from django import forms
from django.core.exceptions import ValidationError

class ContactForm(forms.Form):
    # Everything as before.
    ...

    def clean_recipients(self):
        data = self.cleaned_data["recipients"]
        if "fred@example.com" not in data:
            raise ValidationError("You have forgotten about Fred!")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data
```

#### Nettoyage et validation de champs qui dépendent l’un de l’autre

Supposons que nous ajoutions une autre exigence à notre formulaire de contact : si le champ cc_myself vaut True, le champ subject doit contenir le mot "help". Nous effectuons de la validation s’appliquant à plus d’un champ à la fois, c’est pourquoi la méthode clean() du formulaire est le bon endroit pour cela. Remarquez que nous parlons bien maintenant de la méthode clean() du formulaire, alors qu’auparavant nous avions écrit une méthode clean() pour un champ. Il est important de bien faire la différence entre le champ et le formulaire lorsqu’il s’agit de la validation de contenu. Les champs sont des points de données uniques, les formulaires sont des ensembles de champs.

Au moment où la méthode clean() du formulaire est appelée, toutes les méthodes de nettoyage de chaque champ auront déjà été exécutées (cf. les deux sections précédentes), ce qui fait que self.cleaned_data sera rempli par toute donnée ayant respecté la validation jusque là. Il faut donc aussi se rappeler de tenir compte du fait que les champs que vous souhaitez valider pourraient ne pas avoir passé l’étape préalable de la vérification au niveau du champ individuel.

Il y a deux manières de signaler des erreurs à ce stade. La méthode probablement la plus courante est d’afficher l’erreur au sommet du formulaire. Pour créer une telle erreur, vous pouvez générer une exception ValidationError à partir de la méthode clean(). Par exemple :

```python
from django import forms
from django.core.exceptions import ValidationError

class ContactForm(forms.Form):
    # Everything as before.
    ...

    def clean(self):
        cleaned_data = super().clean()
        cc_myself = cleaned_data.get("cc_myself")
        subject = cleaned_data.get("subject")

        if cc_myself and subject:
            # Only do something if both fields are valid so far.
            if "help" not in subject:
                raise ValidationError(
                    "Did not send for 'help' in the subject despite " "CC'ing yourself."         )
```

Dans ce code, si l’erreur de validation est générée, le formulaire affichera un message d’erreur au sommet du formulaire (dans le cas normal) décrivant le problème. De telles erreurs sont des erreurs non liées à des champs qui sont affichées dans les gabarits par {{ form.non_field_errors }}.

L’appel à `super().clean()` dans l’exemple de code garantit que toute logique de validation dans les classes parentes est conservée. Si votre formulaire hérite d’un autre qui ne renvoie pas de dictionnaire `cleaned_data` dans sa méthode `clean()` (c’est facultatif), n’attribuez pas le résultat de l’appel à super() à cleaned_data et utilisez plutôt `self.cleaned_data` :

```python
def clean(self):
    super().clean()
    cc_myself = self.cleaned_data.get("cc_myself")
    ...
```

La seconde approche pour signaler les erreurs de validation pourrait impliquer d’attribuer le message d’erreur à l’un des champs. Dans ce cas, attribuons un message d’erreur à la fois aux deux lignes « subject » et « cc_myself » dans l’affichage du formulaire. Soyez prudent si vous faites cela en pratique, car cela pourrait amener de la confusion dans la présentation du formulaire. Nous montrons ici ce qui est possible, mais nous vous laissons la responsabilité de constater vous-même ce qui est faisable dans votre contexte particulier. Notre nouveau code (remplaçant l’exemple précédent) ressemble à ceci :

```python
from django import forms

class ContactForm(forms.Form):
    # Everything as before.
    ...

    def clean(self):
        cleaned_data = super().clean()
        cc_myself = cleaned_data.get("cc_myself")
        subject = cleaned_data.get("subject")

        if cc_myself and subject and "help" not in subject:
            msg = "Must put 'help' in subject when cc'ing yourself."
            self.add_error("cc_myself", msg)
            self.add_error("subject", msg)
```

Le second paramètre de add_error() peut être une chaîne, ou de préférence une instance de ValidationError. Consultez Génération de ValidationError pour plus de détails. Notez que add_error() enlève automatiquement le champ de cleaned_data.

#### Génération de ValidationError

Pour une plus grande flexibilité des messages d’erreur et pour qu’il soit plus facile de les surcharger, voici quelques lignes de conduite :

- Fournissez un code d’erreur descriptif au constructeur :
  
  ```python
  # Good
  ValidationError(_("Invalid value"), code="invalid")
  # Bad
  ValidationError(_("Invalid value"))
  ```

- Ne fusionnez pas les variables dans les messages ; utilisez des substituants ainsi que le paramètre params du constructeur :
  
  ```python
  # Good
  ValidationError(
    _("Invalid value: %(value)s"),
    params={"value": "42"},
  )
  # Bad
  ValidationError(_("Invalid value: %s") % value)
  ```

- Préférez la substitution par clé de dictionnaire plutôt que le formatage positionnel. Cela permet de placer les variables dans n’importe quel ordre ou même de les omettre entièrement lors de la réécriture d’un message :
  
  ```python
  # Good
  ValidationError(
    _("Invalid value: %(value)s"),
    params={"value": "42"},
  )
  # Bad
  ValidationError(
    _("Invalid value: %s"),
    params=("42",),
  )
  ```

- Englobez le message dans un appel gettext pour activer sa traduction :

```python
# Good
ValidationError(_("Invalid value"))

# Bad
ValidationError("Invalid value")
Pour résumer le tout :
```

Soit :

```python
raise ValidationError(
    _("Invalid value: %(value)s"),
    code="invalid",
    params={"value": "42"},
)
```

Le respect de ces lignes de conduite est particulièrement utile si vous écrivez des formulaires, des champs de formulaire ou des champs de modèle réutilisables.

Même si ce n’est pas recommandé, si vous vous trouvez à la fin de la chaîne de validation (par ex. la méthode clean() de votre formulaire) et que vous savez que vous n’aurez jamais besoin de surcharger le message d’erreur, vous pouvez toujours opter pour la version plus directe :

ValidationError(_("Invalid value: %s") % value)
Les méthodes Form.errors.as_data() et Form.errors.as_json() bénéficient grandement d’objets ValidationError complètement renseignés (avec un nom code et un dictionnaire params).

#### Génération de plusieurs erreurs¶

Si vous détectez plusieurs erreurs durant une méthode de nettoyage et que vous souhaitiez toutes les signaler à celui qui a soumis le formulaire, il est possible de transmettre une liste d’erreurs au constructeur de ValidationError.

Comme mentionné plus haut, il est recommandé de passer une liste d’instances ValidationError avec les paramètres code et params, mais une liste de chaînes fera aussi l’affaire :

```python
# Good
raise ValidationError(
    [
        ValidationError(_("Error 1"), code="error1"),
        ValidationError(_("Error 2"), code="error2"),
    ]
)

# Bad
raise ValidationError(
    [
        _("Error 1"),
        _("Error 2"),
    ]
)
```
