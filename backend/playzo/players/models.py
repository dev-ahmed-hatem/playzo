from django.db import models
from django.utils.translation import gettext_lazy as _


class Player(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    birthdate = models.DateField(null=True, blank=True, verbose_name=_("Birthdate"))
    gender = models.CharField(max_length=1, choices=Gender.choices, verbose_name=_("Gender"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, unique=True, verbose_name=_("Phone"))
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Location"))
    photo = models.ImageField(
        upload_to="players/photos/",
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )

    # Suggested additional fields
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return self.name
