from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from django.conf import settings


class Player(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player")

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

    # Score-related fields
    total_score = models.IntegerField(default=0, verbose_name=_("Total Score"))
    high_score = models.IntegerField(default=0, verbose_name=_("High Score"))
    games_played = models.IntegerField(default=0, verbose_name=_("Games Played"))
    games_won = models.IntegerField(default=0, verbose_name=_("Games Won"))
    average_score = models.FloatField(default=0.0, verbose_name=_("Average Score"))
    last_game_score = models.IntegerField(null=True, blank=True, verbose_name=_("Last Game Score"))
    last_game_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Game Date"))

    # Suggested additional fields
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return self.name

    def update_score_stats(self, score):
        """Update all score-related statistics when a player finishes a game"""
        from datetime import datetime

        self.last_game_score = score
        self.last_game_date = datetime.now(settings.CAIRO_TZ)
        self.total_score += score
        self.games_played += 1

        if score > self.high_score:
            self.high_score = score

        # Calculate average score
        self.average_score = self.total_score / self.games_played

        self.save()

    def increment_games_won(self):
        """Increment games won count"""
        self.games_won += 1
        self.save()
