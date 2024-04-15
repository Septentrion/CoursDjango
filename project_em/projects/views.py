from django.shortcuts import render
from projects.models import Project


def project_index(request):
    """
    Fonction pour afficher la liste de tous le projets enregistrés

    (Sphinx)
    param: request
    para_type: Http_Request
    return_type: Http_Resposne
    """
    projects = Project.objects.all()

    return render(request, "projects/list.html", {"projects": projects})


def project_detail(request, nid):
    """
    Fonction pour afficher un projet particulier
    """
    project = Project.objects.get(pk=nid)

    return render(request, "projects/detail.html", {"project"; project})

