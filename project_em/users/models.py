from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Defines how the User(or the model to which attached)
    will create users and superusers.
    """
    def create_user(self, email, password, date_of_birth, **extra_fields ):
        """
        Create and save a user with the given email, password,
        and date_of_birth.
        """
        # Si le mail n'est pas défini, déclencher une erreur
        if not email:
            raise ValueError(_("The Email must be set"))

        # Le mail est normalsé (mis en minuscules)
        email = self.normalize_email(email) # lowercase the domain

        # Création de l'objet `CustomUser`
        user = self.model(
            date_of_birth=date_of_birth,
            email=email,
            **extra_fields
        )

        # Hachage du mot de passe
        user.set_password(password) # hash raw password and set

        #Enregistrement deans la base de données
        user.save()
    
        return user

    def create_superuser(self, email, password, date_of_birth, **extra_fields):
        """
        Create and save a superuser with the given email,
        password, and date_of_birth. Extra fields are added
        to indicate that the user is staff, active, and indeed
        a superuser.
        """
        # Fait du groupe 'staff'
        extra_fields.setdefault("is_staff", True)
        # Est une super-utilisateur
        extra_fields.setdefault("is_superuser", True)
        # Le nouvel utilisateur est actif
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                _("Superuser must have is_staff=True.")
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                _("Superuser must have is_superuser=True.")
            )
        return self.create_user(
            email,
            password,
            date_of_birth,
            **extra_fields
        )


class CustomUser(AbstractUser):
    """
    Custom user model which doesn't have a username,
    but has a unique email and a date_of_birth.
    This model is used for both superusers and
    regular users as well.
    """
    # La propriété 'username' est définie dans la classe `AbstractUser`
    # En la nullifiant, on la « supprime » du modèle
    # neither become a DB column nor will it be required.
    username = None

    # Ajout d'un e-mail (avec '_' pour la traduction)
    email = models.EmailField(_("email address"), unique=True)

    # Ajout d'une date de naissance
    date_of_birth = models.DateField(
        verbose_name="Birthday",
        null=True
    )

    # La variable USERNAME_FIELD détermine quelle propriété sera utilisée
    # comme identifiant de connexion
    # Elle remplace 'username' 
    USERNAME_FIELD = "email"
    
    # Ensemble des propriétés obligatoires
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "date_of_birth",
    ]  # The USERNAME_FIELD aka 'email' cannot be included here

    objects = CustomUserManager()
    
    def __str__(self):
        return self.email


