# Bouchons de tests

## Introduction

Lorsque nous voulons faire des tests en isolant la fonctionnalité à tester de son contexte, notamment afin de maîtriser les causes éventuelles des faille, il est possible d'avoir recours à des **bouchons de test**, qui simulent le comportement de vrais objets, dans des conditions que le testeur met explicitement en place.

> Eric Elliott (cf. Ressources) a éccrit un (long mais passionnant) article _contre_ les bouchons de tests.

Dans la pratique, les bouchons de test peuvent servir à :

- se prémunir des alés de fonctionnement d'API externes

- éviter les ralentissements liés à des téléchargements ou des connexions à des SGBD

- simplement fournir une valeur souhaitée

## Implémentation

Depuis Python 3.3, la bibliothèque `mock` a été intégré à la blblithèque standard.

```python
from unittest.mock import Mock
```

La classe `Mock`est le cœur du mécanisme. Elle permet de créer la souche des futurs comportements.

```python
mock = Mock()
```

Nous pouvons maintenant nous servir de cette souche pour remplacer n'importe quelle partie du code, y compris de fonctionnalités standard de Python.

```python
json = mock
```

Admettons que nous voulions simuler le paquetage `json`, nous devrions maintenant décrire les comportements de celui-ci :

```python
# Que pasa ?
json.loads('{"k": "v"}').get('k')
```

Les bouchons de test acceptent n'importe quels arguments et retournent également un boudon de test. Ainsi dans l'exemple ci-dessus, `loads` produit un bouchon qui accepte la méthode `get` et produit un second bouchon.

Nous somme maintenant capables de remplacer une partie quelconque du code de l'application avec quelque chose qui... ne fait rien !

### Maîtriser les bouchons

Nous pouvons, sur cette base, construire le bouchon de test qui correspond à nos besoins.

#### Assigner une propriété

Nous pouvons donner une valeur à une propriété :

```python
fake = Mock()
fake.name = "Personne"
assert "Personne" in fake.name
```

Nous constatons que le comportement du bouchon a changé, car, par défaut l'appel de `fake.name` devrait retourner un bouchon. Mais comme nous avons redéfini cette propriété, nous otenons maintennat la chaîne de caractères que nous voulons.

#### Définir un comportement

De même pour les fonctions, nous pouvons ajouter exactement ce que nous voulons :

```python
def t():
    return datetime.datetime(year=2019, month=1, day=1)

datetime = Mock()
datetime.today = t

assert datetime.today().weekday() = 1
```

Alternativement, il est possible d'utiliser la propriété `side_effect` de `mock` :

```python
datetime = Mock(side_effect=t)
```

Ceci eput être assez pratique pour lever une exception, par exemple.

#### Définir une valeur de retour

Plus simplement, il est possible de définir des valeurs de retour pour des fonctions que nous voudrions utiliser :

```python
t = datetime.datetime(year=2019, month=1, day=1)
datetime = Mock()
datetime.today.return_value = t

assert datetime.today().weekday() = 1
```

### Bouchonner les classes

Jusqu'à présent, nous avons créé des bouchons à l'intérieur d'un module. Mais comment faire pour mettre un bouchon sur un comportement d'un autre module pré-existant ?

`mock` fournit pour cela la fonction `patch`, qui peut s'utiliser comme **décorateur** ou comme **gestionnaire de contexte**.

#### Décorer un appel à un module

Admettons que nous ayons une fonction telle que :

```python
# calendar/holidays.py

import requests

def get_holidays():
    r = requests.get('http://localhost/api/holidays')
    if r.status_code == 200:
        return r.json()
    return None
```

En appelant cette fonction dans un autre module nous pouvons court-circuiter la requête HTTP avec le décorateur :

```python
@patch('<module>.<object>')
```

Par exemple :

```python
import unittest
import json
from calendar import get_holidays
from unittest.mock import patch

class TestCalendar(unittest.TestCase):
    @patch('calendar.requests')
    def test_get_holidays(self, mock_requests):
            mock_requests.get.return_value = json.loads('{}')
            get_holidays()
            # ...
```

#### Le gestionnaire de contexte

De manière équivante, nous pouvons réécrire l'exemple ci-dessus avec un contexte :

```python
import unittest
import json
from calendar import get_holidays
from unittest.mock import patch

class TestCalendar(unittest.TestCase):
    def test_get_holidays(self):
            with patch('my_calendar.requests') as mock_requests:
                mock_requests.get.return_value = json.loads('{}')
                get_holidays()
                # ...
```

#### Utiliser une spécification

Il est possible de bouchonner une classe entière _avec sa composition_, grâce à l'attribut `spec` de `mock`.

```python
from unittest import mock

class A:
  foo = "foo"
  bar = "bar"

  def real_method(self):
    print("The real one")


mock_a = mock.Mock(spec=A)
assert isinstance(mock_a.foo, mock.Mock)
assert isinstance(mock_a.bar, mock.Mock)
assert isinstance(mock_a.real_method, mock.Mock)
assert isinstance(mock_a.real_method(), mock.Mock)

# Déclenchement d'une 'AttributeError'
assert isinstance(mock_a.other_method, mock.Mock)
```

Dans ce cas, l'objet `mock_a` intègre les propriétés et méthodes de la classe `A`. Comme on le voit, toutefois, chacune renvoie un bouchon, c'est-à-dire le comportement par défaut des instances de `Mock`.

### Tester l'exécution des fonctions

Un intérêt des bouchons de test est aussi de pouvoir tester si :

- ils ont été appelés ;
- combien de fois ils ont été appelés ;
- avec quel contexte ils ont été appelés.

Si nous reprenons l'exemple de `json` plus haut, nous pouvons écrire le test suivant :

```python
from unittest.mock import Mock

json = Mock()
# Appel du faux module json
j = json.loads('{"key": "value"}')

# La méthode `loads` a-t-elle été appelée ?
json.loads.assert_called()
# La méthode `loads` a-t-elle été appelée une seule fois ?
json.loads.assert_called_once()
# La méthode `loads` a-t-elle été appelée avec quels arguments ?
json.loads.assert_called_with('{"key": "value"}')
# La méthode `loads` a-t-elle été appelée une seule fois avec quels arguments ?
json.loads.assert_called_once_with('{"key": "value"}')

j = json.loads('{"key": "value"}')
# Le test ne passe plus !
json.loads.assert_called_once()
# `loads` a été appelée deux fois
print(json.loads.call_count)
```

## Ressources

- [Documentation de unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [RealPython à propos de bouchons de test](https://realpython.com/python-mock-library/)
- [Mocking is a code smell — Eric Elliott](https://medium.com/javascript-scene/mocking-is-a-code-smell-944a70c90a6a)
