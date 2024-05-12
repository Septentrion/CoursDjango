# Gestion de profil pour les utilisateurs

## Introduction

## Créer un tableau de bord

Most user management systems have some sort of main page, usually known as a dashboard. You’ll create a dashboard in this section, but because it won’t be the only page in your application, you’ll also create a base template to keep the looks of the website consistent.

You won’t use any of Django’s advanced template features, but if you need a refresher on the template syntax, then you might want to check out Django’s template documentation.

Note: All templates used in this tutorial should be placed in the users/templates directory. If the tutorial mentions a template file users/dashboard.html, then the actual file path is users/templates/users/dashboard.html. For base.html, the actual path is users/templates/base.html, and so on.

The users/templates directory doesn’t exist by default, so you’ll have to create it first. The structure of your project will look like this:

awesome_website/
│
├── awesome_website/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/
│   │
│   ├── migrations/
│   │   └── __init__.py
│   │
│   ├── templates/
│   │   │
│   │   ├── registration/  ← Templates used by Django user management
│   │   │
│   │   ├── users/  ← Other templates of your application
│   │   │
│   │   └── base.html  ← The base template of your application
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── db.sqlite3
└── manage.py

Admettons que nous partions d'une mise en page excessivement simpliste :

```html
<!--users/templates/base.html-->

<h1>Bienvenue sur le site de notre bibliothèque</h1>

{% block content %}
{% endblock %}
```

Créeons un squelette de page très simple pour le tableau de bord des utilisateurs

```html
<!--users/templates/users/dashboard.html-->

{% extends 'base.html' %}

{% block content %}
Hello, {{ user.username|default:'Guest' }}!
{% endblock %}
```

Nopus avons juste à mettre en place le noyau du fonctionnement de la requête, comme habituellement.

```python
# users/views.py

from django.shortcuts import render

def dashboard(request):
    return render(request, "users/dashboard.html")
```

```python
# users/urls.py

from django.conf.urls import url
from users.views import dashboard

urlpatterns = [
    url(r"^dashboard/", dashboard, name="dashboard"),
]
```

```python
# projet/urls.py

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r"^", include("users.urls")),
    url(r"^admin/", admin.site.urls),
]
```

Nous pouvons maintenant lancer le serveur :

```bash
./manage.py runserver
```

Vérifions que nous avons accès aux **deux interfaces** :

- [Tableau de bord pour les utilisateurs](http://localhost:8000/dashboard)
- [Administration pour les super-utilisateurs](http://localhost:8000/admin

### Gestion du profil utilisateur dans Django

A complete website needs a bit more than just a dashboard. Luckily, Django has a lot of user management–related resources that’ll take care of almost everything, including login, logout, password change, and password reset. Templates aren’t part of those resources, though. You have to create them on your own.

Start by adding the URLs provided by the Django authentication system into your application:

```python
# users/urls.py

from django.conf.urls import include, url
from users.views import dashboard

urlpatterns = [
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r"^dashboard/", dashboard, name="dashboard"),
]
```

Nous avons maintenant automatiquement accèz à toute une séride d'URL pourla gestion du profil :

| URL                                | Action                                                        | Nom                     |
| ---------------------------------- | ------------------------------------------------------------- | ----------------------- |
| `accounts/login`                   | Connexion de l'utilisateur                                    | login                   |
| `accounts/logout`                  | Déconnexion de l'utilisateur                                  | logout                  |
| `accounts/password_change`         | Demande de changement de mot de passe                         | password_change         |
| `accounts/password_change/done`    | Changement de mot de passe confirmé                           | password_change_done    |
| `accounts/password_reset`          | Envoi d'un mail avec un lien de remise à zéro du mot de passe | password_reset          |
| `accounts/password_reset/done`     | Affichage de confirmation de l'envoi du mail                  | password_reset_done     |
| `accounts/reset/<uidb64>/<token>/` | Changement du mot de passe via l'URL contenue dans le mail    | password_reset_confirm  |
| `accounts/reset/done`              | Confirmation que le mot de passe à été remis à zéro           | password_reset_complete |

#### Créer une page de connexion

For the login page, Django will try to use a template called registration/login.html. Go ahead and create it:

```html
<!--users/templates/registration/login.html-->

{% extends 'base.html' %}

{% block content %}
<h2>Login</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" value="Login">
</form>

<a href="{% url 'dashboard' %}">Back to dashboard</a>
{% endblock %}
```

This will display a Login heading, followed by a login form. Django uses a dictionary, also known as a context, to pass data to a template while rendering it. In this case, a variable called form will already be included in the context—all you need to do is display it. Using {{ form.as_p }} will render the form as a series of HTML paragraphs, making it look a bit nicer than just {{ form }}.

The {% csrf_token %} line inserts a cross-site request forgery (CSRF) token, which is required by every Django form. There’s also a button for submitting the form and, at the end of the template, a link that will take your users back to the dashboard.

You can further improve the looks of the form by adding a small CSS script to the base template:

```html
<!--users/templates/base.html-->

<style>
    label, input {
        display: block;
    }
    span.helptext {
        display: none;
    }
</style>

<h1>Welcome to Awesome Website</h1>

{% block content %}
{% endblock %}
```

By adding the above code to the base template, you’ll improve the looks of all of your forms, not just the one in the dashboard.

You can now open http://localhost:8000/accounts/login/ in your browser, and you should see something like this:
Login page

Use the credentials of your admin user and press Login. Don’t be alarmed if you see an error screen:
Missing user profile url in Django

According to the error message, Django can’t find a path for accounts/profile/, which is the default destination for your users after a successful login. Instead of creating a new view, it would make more sense to reuse the dashboard view here.

Luckily, Django makes it easy to change the default redirection. All you need to do is add one line at the end of the settings file:

```python
# awesome_website/settings.py

LOGIN_REDIRECT_URL = "dashboard"
```

Try to log in again. This time you should be redirected to the dashboard without any errors.

#### Déconnexion

Pour la déconnexion, le processus est plus simple qpuisqu'il ne nécessite pas de formulaire. Ajoutons juste une route de retour dabs le fichier `settings.py` :

```python
# awesome_website/settings.py

LOGOUT_REDIRECT_URL = "dashboard"
```

Mettons à jour notre mise en page pour permettre à l'utilisateur de de dédonnecter :

```twig
{# users/templates/users/dashboard.html #}
{% extends 'base.html' %}

{% block content %}
Hello, {{ user.username|default:'Guest' }}!

<div>
    {% if user.is_authenticated %}
        <a href="{% url 'logout' %}">Déconnexion</a>
    {% else %}
        <a href="{% url 'login' %}">Identifiez-vous</a>
    {% endif %}
</div>
{% endblock %}
```

#### Changement de mot de passe

Vous voudrez sans doute donner la possibilité à vos utilisateurs de changer de mot de passe. Pour cela, vous aurez besoin de deux écrans :

| Chemin                                   | Usage                                  |
| ---------------------------------------- | -------------------------------------- |
| `registration/password_change_form.html` | Le formulaire de changement            |
| `registration/password_change_done.html` | La page de confirmation du chgangement |

Voici un exemple pour la première page :

```twig
{# users/templates/registration/password_change_form.html #}
{% extends 'base.html' %}

{% block content %}

<h2>Changement du mot de passe</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" value="Changer">
</form>

<a href="{% url 'dashboard' %}">Retour au tableau de bord</a>
{% endblock %}
```

Pour la seconde :

```twig
{# users/templates/registration/password_change_done.html #}
{% extends 'base.html' %}

{% block content %}

<h2>Votre mot de passe a bien été modifié</h2>

<a href="{% url 'dashboard' %}">Retour au tableau de bord</a>
{% endblock %}
```

Eventuellemen, incluez un lien sur le tableau de bord :

```twig
{# users/templates/users/dashboard.html #}
{% extends 'base.html' %}

{% block content %}
Hello, {{ user.username|default:'Guest' }}!

<div>
    {% if user.is_authenticated %}
        <a href="{% url 'logout' %}">Déconnexion</a>
        <a href="{% url 'password_change' %}">Changement de mot de passe</a>
    {% else %}
        <a href="{% url 'login' %}">Identifiez-vous</a>
    {% endif %}
</div>
{% endblock %}
```

> [!NOTE]
> Notez que si vous n'êtes pas connecté, Django vous redirigera automatiquement vers la page de connexion

#### Envoyer un lien de remise à zéro du mot de passe

Si vous avez oublié votre mot de passe, la méthode précédente ne vous sera d'aucune utilité. Dans ce cas, on demande généralement à recevoir un mail pour réinitialiser le mot de passe du compte.

> [!IMPORTANT]
> Pour effectuer des tests, vous pouvez lancer un serveur SMTP factice avec cette commande :
> 
> ```bash
> python -m smtpd -n -c DebuggingServer localhost:1025
> ```
> 
> Vous pourrez lire les contenus de mails dans le terminal et ainsi récupérer l'URL qui vous servira à réinitaliser le mot de passe.
> Vous avez juste à ajouter ces lignes dans le fichier `settings.py` :
> 
> ```python
> # projet/settings.py
> ```

> EMAIL_HOST = "localhost"
> EMAIL_PORT = 1025
> 
> ```
> 
> ```

Là encore, nous allons avoir besoin de deux écrans.

| Chemin                                  | Usage                                      |
| --------------------------------------- | ------------------------------------------ |
| `registration/password_reset_form.html` | Le formulaire de requête                   |
| `registration/password_reset_done.html` | La page de confirmation de l'envoi du mail |

Ils sont très semblables à ceux écrits pour le changement de mot de passe :

```twig
{# users/templates/registration/password_reset_form.html #}
{% extends 'base.html' %}

{% block content %}

<h2>Recevoir un mail de réinitalisation de votre mot de passe</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" value="Réinitialiser">
</form>

<a href="{% url 'dashboard' %}">Retour au tableau de bord</a>
{% endblock %}
```

Puis :

```twig
{# users/templates/registration/password_reset_done.html #}
{% extends 'base.html' %}

{% block content %}

<h2>Un mail vous a été envoyé</h2>

<a href="{% url 'login' %}">Retour à la page de connexion</a>
{% endblock %}
```

Et vous pouvez ajouter un lien sur la page de connexion:

```twig
{# users/templates/registration/login.html #}

{% extends 'base.html' %}

{% block content %}

<h2>Login</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" value="Login">
</form>

<a href="{% url 'dashboard' %}">Retour au tableau de bord</a>
<a href="{% url 'password_reset' %}">Réinitaliser le mot de passe</a>
{% endblock %}
```

Le mail de requête devrait ressembler à quelque chose comme :

```text
---------- MESSAGE FOLLOWS ----------
b'Content-Type: text/plain; charset="utf-8"'
b'MIME-Version: 1.0'
b'Content-Transfer-Encoding: 7bit'
b'Subject: Password reset on localhost:8000'
b'From: webmaster@localhost'
b'To: admin@example.com'
b'Date: Wed, 22 Apr 2020 20:32:39 -0000'
b'Message-ID: <20200422203239.28625.15187@pawel-laptop>'
b'X-Peer: 127.0.0.1'
b''
b''
b"You're receiving this email because you requested a password reset for your
user account at localhost:8000."
b''
b'Please go to the following page and choose a new password:'
b''
b'http://localhost:8000/accounts/reset/MQ/5fv-f18a25af38f3550a8ca5/'
b''
b"Your username, in case you've forgotten: admin"
b''
b'Thanks for using our site!'
b''
b'The localhost:8000 team'
b''
------------ END MESSAGE ------------
```

#### Remttre à zéro le mot de passe

Django vous a envoyé un mail pour que vouspuissiez remettre à zéro votre mot de passe. Nous avons maintenant besoin de pages pour effectuer cette manœuvre: 

| Chemin                                     | Usage                                                 |
| ------------------------------------------ | ----------------------------------------------------- |
| `registration/password_reset_confirm.html` | Le formulaire de réinitialisation                     |
| `registration/password_reset_done.html`    | La page de confirmation du changement de mot de passe |

Là encore, rien de très origine :

```twig
{# users/templates/registration/password_reset_confirm.html #}
{% extends 'base.html' %}

{% block content %}

<h2>Réinitialisez votre mot de passe</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" value="Confirmer le changement">
</form>
{% endblock %}
```

Et :

```twig
{# users/templates/registration/password_reset_complete.html #}
{% extends 'base.html' %}

{% block content %}

<h2>Votre mot de passe a bien été modifié</h2>

<a href="{% url 'login' %}">Veuillez vous reconnecter</a>
{% endblock %}
```

Le processus est maintenant totalement achevé.

##### Personnaliser le gabarit du mail

Vous pouvez naturellement changer la présentation des mails :

- `registration/password_reset_email.html` pour le corps du mail
- `registration/password_reset_subject.txt` pour le sujet du mail

Voici un exemple de squelette d'email avec les variables que vous pouvez utiliser :

```twig
{# users/templates/registration/password_reset_email.html #}

Someone asked for password reset for email {{ email }}.
Follow the link below:
{{ protocol}}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}
```

Vous verriez alors apparaître ceci :

```text
---------- MESSAGE FOLLOWS ----------
b'Content-Type: text/plain; charset="utf-8"'
b'MIME-Version: 1.0'
b'Content-Transfer-Encoding: 7bit'
b'Subject: Reset password'
b'From: webmaster@localhost'
b'To: admin@example.com'
b'Date: Wed, 22 Apr 2020 20:36:36 -0000'
b'Message-ID: <20200422203636.28625.36970@pawel-laptop>'
b'X-Peer: 127.0.0.1'
b''
b'Someone asked for password reset for email admin@example.com.'
b'Follow the link below:'
b'http://localhost:8000/accounts/reset/MQ/5fv-f18a25af38f3550a8ca5/'
------------ END MESSAGE ------------
```

### Création d'un nouvel utilisateur

Nous avons maintenant à peu près tout ce qu'il nous faut... hormis la possibilité de s'inscire sur le site.

Django n'ayant pas deressource propre pur cela, nous allons devoir nous-mêmes créer la chaîne d'inscription.

Django offers a lot of forms that you can use in your projects. One of them is UserCreationForm. It contains all the necessary fields to create a new user. However, it doesn’t include an email field.

In many applications, this might not be a problem, but you’ve already implemented a password reset feature. Your users need to configure an email address or else they won’t be able to receive password reset emails.

To fix that, you need to add your own user creation form. Don’t worry—you can reuse almost the entire UserCreationForm. You just need to add the email field.

Create a new Python file called users/forms.py and add a custom form there:

```python
# users/forms.py

from django.contrib.auth.forms import UserCreationForm

class LibraryUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
```

As you can see, your `LibraryUserCreationForm` extends Django’s UserCreationForm. The inner class `Meta` keeps additional information about the form and in this case extends UserCreationForm.Meta, so almost everything from Django’s form will be reused.

The key difference is the fields attribute, which determines the fields that’ll be included in the form. Your custom form will use all the fields from UserCreationForm and will add the email field.

Now that the form is ready, create a new view called register:

```python
# users/views.py

from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import CustomUserCreationForm

def dashboard(request):
    return render(request, "users/dashboard.html")

def register(request):
    # Affichage du formulaire d'enregistrement 
    if request.method == "GET" :
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )
    # Traitement du formulaire
    # Si les données sont valides, l'utilisateur est créé
    # puis automatiquement connecté
    # et redirigé vers son tableau de bord
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))
```

Le formulaire pourrait ressembler à ceci :

```twig
{# users/templates/users/register.html #}
{% extends 'base.html' %}

{% block content %}
<h2>Inscription</h2>
<form method="post">
    {% csrf_token %}
    {{form}}
    <input type="submit" value="Inscription">
</form>
<a href="{% url 'login' %}">REtour à la page de connexion</a>
{% endblock %}
```

Il ne reste qu'à enregistrer la route :

```python
# users/urls.py

from django.conf.urls import include, url
from users.views import dashboard, register

urlpatterns = [
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r"^dashboard/", dashboard, name="dashboard"),
    url(r"^register/", register, name="register"),
]
```

Et à actualiser la page d'accueil :

```twig
{# users/templates/registration/login.html #}
{% extends 'base.html' %}

{% block content %}
<h2>Connexion</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" value="Login">
</form>

<a href="{% url 'dashboard' %}">Retour au tableau de bord</a>
<a href="{% url 'password_reset' %}">Réinitialiser lemot de passe</a>
<a href="{% url 'register' %}">Inscrivez-vous</a>
{% endblock %}
```
