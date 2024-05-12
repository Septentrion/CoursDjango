# Tests d'intégration avec Django

## Introduction

Au-delà des fonctionnalités atomiques, nous vaons besoin de tester des scénarios utilsateurs, intégrant des requêtes HTTP sur l'API de l'application.
Il existe plusieurs manières de réaliser cette opération.

## Tester une vue avec le client Django

Django intègre nativment un client qui permet d'exécuter des requêtes sur des URL.
Cela peut d'avérer très utile pour tester nos vues.

Admetons que nous ayons une vue dépondant à une route donnée :

```python
# urls.py
from django.urls import path

from . import views

urlpatterns = [
    # ex: /books/
    path("/books", views.index, name="book_index"),
]
```

Cette vue est censée afficher une liste de livres contenue dans la base de données.

Nous pouvons écrire la classe de tests suivqante :

```python
# library/tests/test_view.py

from django.test import TestCase
from django.urls import reverse
from datetime import datetime

from catalog.models import Author

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Créons 10 livres pour les tests
        # Les valeurs doivent être maîtrisées
        pool_size = 10

        for id in range(pool_size):
            Book.objects.create(
                title=f'Titre {id}',
                acquisition_date=datetime.today()
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/books')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('book_index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('book_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 3)
```

## Tester avec Selenium

Une solution plus générale consiste à choisir le client de test à utiliser. **Selenium**, par exemple, est un moteur très roubuste et utilsé de puis très longtemps. Il offre davantage des possibilités de t'ests réalistes que le client natif (dit « _dummy_ ») de Django.

La meilleur manière de procéder est d'utiliser la classe `LiveServerTestCase`. Celle-ci n'est pas très différente de `TestCase`, à ceci près que le moteur de test s'exécute dans un thread différent de celui de Django. Ce qui permet :

1. d'utiliser un client de test arbitraire

2. de réaliser de « _vraies_ » requêtes HTTP puisque nous avons deux processus différents qui s'exécutent en parallèle.

Dans un premier temps, il faut installer Selenium, comme un paquetage Python :

```bash
pip install selenium
```

Seleium offre des fonctinnalités plus avancées que le client Django. Néanmoins, cela reste un simulateur. Il nous permettra de tester :

- l'apparence des pages,
- l'envoi de formulaires
- la navigation via des liens hypertextes
- diférents navigateurs

Une classe de tests de base s'écrit ainsi :

```python
# library/tests/test_view.py

from selenium import webdriver
from django.test import LiveServerTestCase

class TestSignup(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        """
        Le navigateur virtuel est lancé une fois pour toutes
        """
        super.setUpClass()
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(10)

    def test_signup_fire(self):
        # Envoie d'une requête sur un URL
        # Notez la propriété qui 
        self.driver.get(f"{self.live_server_url}/books/")
        # Teste la validité de l'URL
        self.assertIn("http://localhost:8000/", self.driver.current_url)

    @classmethod
    def tearDownClass(self):
        """
        Le navigateur virtuel est éteint à la fin des tests
        """
        cls.driver.quit()
        super.tearDownClass()
```

### Trouver un élément dans la page

Selenium possède un module `By`, qui permet de chercher des éléments dans la page selon une de leurs caractéristiques. Par exemple :

```python
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("http://www.python.org")
elem = driver.find_element(By.NAME, "q")
```

La méthode `find_element` rend le premier élément trouvé. Si vous souhaitez avoir la toutalité des éléments (tous les liens hypertextes, par exemple), utilisez `find_elements`.

Voilà la liste des critères utilsables:

| Nom               | Signification                 |
| ----------------- | ----------------------------- |
| ID                | attribut `id` de l'élément    |
| NAME              | attribut `name` de l'élément  |
| XPATH             | chemin **XPATH** de l'élément |
| LINK_TEXT         | texte du lien                 |
| PARTIAL_LINK_TEXT | fragment du texte du lien     |
| TAG_NAME          | nom de la balise HTML         |
| CLASS_NAME        | classe CSS                    |
| CSS_SELECTOR      | sélecteur CSS                 |

### Rempir un formulaire

 Il est aussi tout à fait posible de remplir un formulaire.

 Renons le cas d'un formulaire de recherche. Nous voudrions pouvoir fournie à un utilsateur une liste de livres dont le titre contient un certain mot :

```python
from selenium.webdriver.common.keys import Keys
# ...
search_form = driver.find_element(By.ID, "search_text")
# Rafraîchissment du champ
elem.clear()
# Simulation d'une saisie au clavier
elem.send_keys("Ulysse")
# Simulation d'envoi avec appui sur la touche <RETURN>
elem.send_keys(Keys.RETURN)
# Tester que des résultats ont bien été trouvés
assert "No results found." not in driver.page_source
# ...
```

### Suivre un lien

Nous pouvons également tester que les liens hypertyextes sont bien actifs.

```python
# Recherche du lien
detail_link = driver.find_element(By.LINK_TEXT, "Afficher le livre 1248")
# Envoi de la requête
detail_link.click()
# Test de la nouvelle page
assert "Ulysse" in driver.find_element(By.TAG_NAME, "title")
```

Voici un exemple de test de connexion :

```python
    def test_login(self):
        # Afficher le formulaire de connexion
        self.selenium.get(f"{self.live_server_url}/login/")
        # Trouver le champ dont le nom est 'username'
        username_input = self.selenium.find_element(By.NAME, "username")
        # Remplir le champs avec son identifiant
        username_input.send_keys("Me")
        # Trouver le champ dont le nom est 'password'
        password_input = self.selenium.find_element(By.NAME, "password")
        # Remplir le champ avec son mot de passe
        password_input.send_keys("secret")
        # Trouver le boutn submit dont le texte est 'Log in'
        # Et cliquer pour envoyer le formulaire
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()
        # Tester la réponse
        # Malheureusement, il n'y a pas de moyen simple 
        # de tester le code de statut HTTP
        identifier = selenium.find_element(By.ID, 'username_block')
        element_text = identifier.text
        self.assertEqual(element_text, 'Me')       
```

## Ressources

- [Le client Django](https://docs.djangoproject.com/en/5.0/topics/testing/tools/)
- [Selenium pour Python](https://selenium-python.readthedocs.io/)
