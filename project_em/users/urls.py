from django.urls import path
from django.conf.urls import include
# from django.conf.urls import url
from users import views

urlpatterns = [
    # famille de routes pour la gestion 
    # - de la connexion, 
    # - de la déconnexion
    # - du changement de mot de passe
    path("accounts/", include("django.contrib.auth.urls")),
    # Un URL pour un tableau de bord
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
]
