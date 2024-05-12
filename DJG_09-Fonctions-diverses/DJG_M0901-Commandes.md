# Écriture de commandes personnalisées

## Introduction

Les applications peuvent inscrire leurs propres actions auprès de `manage.py`. 

Dans ce document, nous allons créer un commande personnalisée `suspendaccount` qui permettra à un administrateur de suspendre un compte utilsateur, pour les lecteurs qui ont trop de retard, par exemple. Cette action pourrait naturellement être exécutée dans une interface graphique d'administration, mais la ligne de commande nous permet d'automatiser le processus ou de lier notre application à d'autres applications. C'est en quelque sorte une autre forme d'API pour cette application, indépendante du web.

> [!NOTE]
> Cette page est inspirée de la documentation officielle.

## Préparation

Pour commentcer, ajoutons un répertoire `management/commands` dans l’application. 
Django inscrit une commande `manage.py` pour chaque module Python dans ce répertoire dont le nom **ne commence pas** par le caractère '\_'. Par exemple :

```
accounts/
    __init__.py
    models.py
    management/
        __init__.py
        commands/
            __init__.py
            _private.py
            suspendaccount.py
    tests.py
    views.py
```

Dans cet exemple, la commande `suspendaccount` sera disponible dans tout projet qui inclut l’application `accounts`  dans sac configuration `INSTALLED_APPS`.

- Le module `_private.py`, lui,  ne sera pas disponible en tant que commande de gestion.

- Le module `suspendaccount.py` n’a qu’une seule exigence : il doit définir une classe `Command` comme sous-classe de `BaseCommand`, ou l’une de ses sous-classes.

## Implémentation

Les commandes personnalisées sont particulièrement utiles pour exécuter des scripts autonomes ou pour des scripts qui sont programmés pour s’exécuter périodiquement par l’intermédiaire du *crontab Unix*, par "exemple.

Pour implémenter la commande, commençons par créer le squelette de la commande dans le fichier `suspendaccount.py` comme ceci :

```python
# accounts/management/commands/suspendaccount.py

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    # Définition des arguments de la commande
    def add_arguments(self, parser):
       pass

    # Code fonctionnel de la commande
    def handle(self, *args, **options):
        pass
```

D'emblée, nous avons deux fonctions essentielles :

- `add_arguments()`, qui définit l'interaction avec l'utilisateur par la ligne de commande, lors du lancement de la commande

- `handle()`, qui contient tout le code nécesaire à l'achèvement de la commande.

Nous définissons également la proprété `help` qui servira à afficher un texte court de documentation dans le terminal.

### Définition de paramètres facultatifs

Nous allons maintenant devoir définir les arguments que l'utilisateur peut passer à la commande lors de son lancement. Ces arguments peuvent être de deux types :

- positionnels

- nommés (facultatifs)

La commande que nous voulons écrire amettrait un ou plusieurs numéros de lecteurs (leur identifiant). Et pour ces lecteurs indélicats, nous souhaitions indiquer 

- une durée de suspension du compte (en nombre de jours)

- l'envoi optionnel d'un mail de relance

```python
# accounts/management/commands/suspendaccount.py

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Argument positionnel
        # Nous fournissons :
        # - le nom d'une variable pour la fonction `handle()`
        # - l'arité de l'argument 
        #    -- ici '+' sigfnifie 1 ou plus, ce qui produit une liste
        # - le type des données
        #    -- on suppose ici une chaîne de caractères genre UUID
        parser.add_argument("reader_ids", nargs="+", type=str)

        # Argument nommé
        # Nous fournissons :
        # - l'étiquette assiociée à l'arguemnt
        # - l'action associée : store_true`
        # - un texte d'aide pour la description de la commande
        parser.add_argument(
            "--duree",
            help="Nombre de jours de suspension du compte",
        )

        # - l'action associée `store_true` indique que l'option a pour valeur `True`
        parser.add_argument(
            "--relance",
            action="store_true",
            help="Un mial doit ",
        )

    def handle(self, *args, **options):
        pass
```

Les arguments de `manage.py` fonctionnent selon les règles du paqutage `argparse` de Python. Vous pouvez donc vous référer la la documentation de cette bibliotthèque pour les détails d'implémentation.

Les arguments seront par la suite disponibles pour la finction `handle()` via un dictionnaire `options`.

### Le corps de la commande

Il nous reste maintenant à écrire la fonctionnalité elle-même de la commande, c'est-à-dire le corps de la méthode `handle()`.

```python
# accounts/management/commands/suspendaccount.py

from django.core.management.base import BaseCommand, CommandError
frome datetime import datetime, datedelta
from accounts.models import Reader
from utils import send_warning_mail

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        # Code omis

    def handle(self, *args, **options):
        # Il peut y avoir plusieurs lecteurs concernés
        # Nous devons donc parcourir la liste
        for id in options["reader_ids"]:
            try:
                account = Reader.objects.get(pk=id)
            # Si un identifiant est erroné, on déclenche une exception
            # Une manière moins expéditive consisterait à juste passer au suivant
            except Reader.DoesNotExist:
                raise CommandError(f"Aucun compte {id} n'existe dans la base de données.")

            # Nous calculons la date à laquelle le compte redeviendra actif
            # Si aucune valeur n'est donnée, nous prnons par défaut 30 jours
            duration = options["duree"] if options["duree"] else 30
            account.suspended_until = datetime.datetime.now() + timedelta(days=duration)

            # Les données sont sauvegardées
            # Le modèle s'occupe de tout
            account.save()

            # Affichage d'un message de notification de réussite
            self.stdout.write(
                self.style.SUCCESS(f"Le lecteur {id} est suspendu jusqu’au : {account.suspended_until}.")
            )

            # Optionnellement, nous envoyons un mail
            # Cet envoir pourrait
            if options["relance"):
                send_warning_mail(account.email)
                self.stdout.write(
                    self.style.SUCCESS(f"Un mail a été envoyé à {account.email}.")
```

That's it !

>  [!NOTE]
> Quand vous utilisez des commandes et que vous souhaitez afficher des informations en console, vous devrez utiliser les méthodes `self.stdout` et `self.stderr` plutôt que d’utiliser directement `stdout` et `stderr`. En utilisant ces méthodes intermédiaires, il devient beaucoup plus simple de tester vos commandes personnalisées. Notez aussi que vous n’avez pas besoin de terminer vos messages avec un caractère de saut de ligne car il sera ajouté automatiquement, sauf si vous indiquez le paramètre ending:
>  ```self.stdout.write("Unterminated line", ending="")```

La nouvelle commande personnalisée peut être appelée en utilisant :

```bash
./manage.py suspendaccount 253 1245 2416 --duree 14
```

### Tests

Les commandes étant des modules comme les autres, les techniques de tests de diffèrent pas des celles utilisées traditionnellement en Python.

## Compléments

### Commandes de gestion et langues

Par défaut, les commandes d’administration sont exécutées avec la langue active. Si pour une raison quelconque, votre propre commande d’administration doit fonctionner sans langue active (par exemple pour empêcher du contenu traduit d’être inséré dans la base de données), désactivez toute traduction en appliquant le décorateur `@no_translations` à votre méthode `handle()`:

```python
from django.core.management.base import BaseCommand, no_translations

class Command(BaseCommand):
    # ...

    @no_translations
    def handle(self, *args, **options):
        pass
```

Comme la désactivation des traductions nécessite d’accéder aux réglages configurés, ce décorateur ne peut pas être utilisé pour des commandes qui doivent fonctionner même si les réglages ne sont pas configurés.

### Surcharge des commandes

Django enregistre les commandes intégrées et recherche ensuite les commandes dans **l’ordre inverse** des déclarations dans `INSTALLED_APPS`. Pendant la recherche, si le nom d’une commande est un duplicata d’une commande déjà enregistrée, la commande nouvellement découverte surcharge la première.

En d’autres termes, pour surcharger une commande, la nouvelle commande doit avoir le même nom et son application doit se trouver avant l’application de la commande dont on souhaite la surcharge dans INSTALLED_APPS.

## Objets de commandes

### class BaseCommand

La classe de base dont toutes les autres commandes de gestion héritent.

Utilisez cette classe si vous souhaitez accéder à tous les mécanismes qui analysent les paramètres de ligne de commande et qui aiguillent sur le code à appeler en conséquence. Si vous n’avez pas besoin de modifier ce comportement, considérez l’utilisation de l’une de ses sous-classes.

L’héritage direct de la classe `BaseCommand` exige que vous implémentiez la méthode handle().

### Attributs

Tous les attributs peuvent être définis dans votre sous-classe et peuvent être utilisés dans les sous-classes de BaseCommand.

| Attribut                     | Utilisation                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `help`                       | Une brève description de la commande, qui sera affichée dans le message d’aide lorsque l’utilisateur lance la commande python `manage.py help <commande>`.                                                                                                                                                                                        |
| `missing_args_message`       | Si votre commande définit des paramètres positionnels obligatoires, vous pouvez personnaliser le message d’erreur renvoyé au cas où le paramètre serait absent. Le message par défaut est produit par argparse (« too few arguments » (trop peu de paramètres)).                                                                                  |
| `output_transaction`         | Une valeur booléenne indiquant si la commande affiche des commandes SQL ; si True, le contenu en sortie est automatiquement entouré des instructions BEGIN; et COMMIT;. La valeur par défaut est `False`.                                                                                                                                         |
| `requires_migrations_checks` | Valeur booléenne ; si True, la commande affiche un avertissement si le jeu de migrations sur disque ne correspond pas aux migrations dans la base de données. Un avertissement n’empêche pas la commande de s’exécuter. La valeur par défaut est `False`.                                                                                         |
| `requires_system_checks`     | Une liste ou un tuple d’étiquettes, par ex. `[Tags.staticfiles, Tags.models]`. Les contrôles système inscrits avec les étiquettes indiquées seront exécutés avant d’exécuter la commande. La valeur '\_\_all\_\_' peut être utilisée pour indiquer que tous les contrôles système doivent être appliqués. La valeur par défaut est '\_\_all\_\_'. |
| `suppressed_base_arguments`  | Les options de commande à supprimer par défaut dans l’affichage de l’aide. Cela doit être un ensemble de noms d’options (par ex. '--verbosity'). Les valeurs par défaut des options supprimées sont tout de même transmises.                                                                                                                      |
| `style`                      | Un attribut d’instance aidant à colorer le contenu envoyé aux sorties stdout ou stderr.                                                                                                                                                                                                                                                           |

> [!NOTE]
> `self.stdout.write(self.style.SUCCESS("..."))`
> cf. la syntaxe colorée pour savoir comment modifier la palette de couleurs et pour connaître les styles disponibles (utilisez les versions en majuscules des « rôles » décrits dans cette section). Si vous passez l’option `--no-color` lors du lancement de la commande, tous les appels à self.style() renverront la chaîne originale sans couleur.

## Ressources

- [Documentation officielle](https://docs.djangoproject.com/fr/5.0/howto/custom-management-commands/)
- [Documentation de 'argparse](https://docs.python.org/3/library/argparse.html)
- [Tutoriel à propos de 'argparse'](https://realpython.com/command-line-interfaces-python-argparse/)
