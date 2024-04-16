from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Defines how the User(or the model to which attached)
    will create users and superusers.
    """
    def create_user(
        self,
        email,
        password,
        date_of_birth,
        **extra_fields
        ):
        """
        Create and save a user with the given email, password,
        and date_of_birth.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email) # lowercase the domain
        user = self.model(
            date_of_birth=date_of_birth,
            email=email,
            **extra_fields
        )
        user.set_password(password) # hash raw password and set
        user.save()
        return user
    def create_superuser(
        self,
        email,
        password,
        date_of_birth,
        **extra_fields
        ):
        """
        Create and save a superuser with the given email,
        password, and date_of_birth. Extra fields are added
        to indicate that the user is staff, active, and indeed
        a superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
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
    # The inherited field 'username' is nullified, so it will
    # neither become a DB column nor will it be required.
    username = None
    email = models.EmailField(_("email address"), unique=True)
    date_of_birth = models.DateField(
        verbose_name="Birthday",
        null=True
    )
    # Set up the email field as the unique identifier for users.
    # This has nothing to do with the username
    # that we nullified above.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "date_of_birth",
    ]  # The USERNAME_FIELD aka 'email' cannot be included here
    objects = CustomUserManager()
    def __str__(self):
        return self.email



