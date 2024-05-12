# Les vues dans Django

## Introduction

En premier lieu, il faut considérer que les « _vues_ » de Django ne sont pas des gabarçits d'affichage.
En réalité, ce sont plutôit des « _contrôleurs_ », au sens où il sont les exécutants de la requête envoyée par l'utilisateur.

## Vues

### Une première vue

Les vues sont compilées dans le fichier `views.py`.
On peut écrire de la amnière la plus simple :

```python
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello ! Vous êtes sur la page d'accueil de notre site.")
```

En admettant que nous ayons conservé le fichier de routage décrit dans `DJG_M01-Routage`, nous avons ici une fonction `index` qui correspond à la racine de l'application (le routeur s'attend à trouver cette fonction).

1. La fonction index reçoit un argument qui contient les éléments de la requête.
2. On va chercher dans le module `http` la classe `HttpResponse` qui permettra d'envoyer une réponse à l'utilisateur.

> ![NOTE]
> Naturellement, vous pouvez passer à `HttpResponse` toute expression Pythin légitime

### Gabarits d'affichage

En général, nous voudrons :

- soit envoyer des pages HTML dans le cas d'une application web classique ;
- soit — ce qui n'est pas incompatible — envouyer un lot de données si nous sommes en mode API.

Nous considérons ici le premier cas de figure.

Pour décrire les pages HTML, **Django** intègre **Jinja** qui est un moteur de rendu, très proche de **Twig** pour les applications PHP.

Par défaut, tous les gabarrits d'affichage se trouvent dans le dossier `templates/`.

> ![NOTE]
> Vous pouvez changer cela avec la variblade configuration du projet, dans le fichier `settings.py`.
> Vous devrez modifier la constante TEMPLATES

Un fichier Jinja se présente de ctte façon :

```jinja
{% if latest_question_list %}
    <ul>
    {% for question in latest_question_list %}
        <li><a href="/polls/{{ question.id }}/">{{ question.question_text }}</a></li>
    {% endfor %}
    </ul>
{% else %}
    <p>No polls are available.</p>
{% endif %}
```

> Pour davantage de précisions, repotez-vous à la documentation de Jinja

Maintenant que nous avons défini un format d'affichage, il ne reste qu'à le déclarer dans la vue :

```python
from django.http import HttpResponse
from django.template import loader
from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("polls/index.html")
    context = {
        "latest_question_list": latest_question_list,
    }
    return HttpResponse(template.render(context, request))
```

ou, plus simplement :

```poython
from django.shortcuts import render
from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)
```

### Cas des pages d'erreur

Si la ressource demandée n'existe pas, nous pouvons renvoyer une réponse apporpriée. LA aussi, Django offre une alternative :

```python
from django.http import Http404
from django.shortcuts import render

from .models import Question


# ...
def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/detail.html", {"question": question})
```

ou plus simplement :

```python
from django.shortcuts import get_object_or_404, render

from .models import Question


# ...
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})
```

### Engendrement des URL

COmme dans tous les environnements d'applications, nous éviterons de coder des URL « _en dur_ » dans le code.
A la place, il vaudra meiux écrire :

```jinja
<li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>
```

en utilisant l'instruction `url`, associée au n om de la route, tel que défini dans le fichier `urls.py`.

Si vous avez déclaré un espace de noms pour les routes de l'application, vous pouvez l'utiliser ici :

```jinja
<li><a href="{% url 'polls:detail' question.id %}">{{ question.question_text }}</a></li>
```

## Ressources

- [Documentation de Jinja]()
