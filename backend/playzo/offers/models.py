from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from players.models import Player
from users.models import User


class Offer(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        UPCOMING = "UPCOMING", _("Upcoming")
        EXPIRED = "EXPIRED", _("Expired")
        DRAFT = "DRAFT", _("Draft")

    class OfferType(models.TextChoices):
        DISCOUNT = "DISCOUNT", _("Discount")
        EVENT = "EVENT", _("Event")
        TRAINING = "TRAINING", _("Training")
        MEMBERSHIP = "MEMBERSHIP", _("Membership")
        OTHER = "OTHER", _("Other")

    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"), blank=True)

    # Visual properties
    color = models.CharField(
        max_length=7,
        default="#1565C0",
        verbose_name=_("Color"),
        help_text=_("Hex color code (e.g., #1565C0)")
    )
    image = models.ImageField(
        upload_to="offers/images/",
        verbose_name=_("Image"),
        blank=True,
        null=True
    )
    image_url = models.URLField(
        verbose_name=_("Image URL"),
        blank=True,
        null=True,
        help_text=_("External image URL (overrides uploaded image if provided)")
    )

    # Offer details
    offer_type = models.CharField(
        max_length=20,
        choices=OfferType.choices,
        default=OfferType.OTHER,
        verbose_name=_("Offer Type")
    )

    # Validity
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Status")
    )

    # Target audience
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured Offer")
    )
    is_exclusive = models.BooleanField(
        default=False,
        verbose_name=_("Exclusive Offer")
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="offers_created",
        verbose_name=_("Created By")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = _("Offer")
        verbose_name_plural = _("Offers")

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """Check if offer is currently active"""
        from datetime import datetime
        now = datetime.now(settings.CAIRO_TZ)
        return (
                self.status == self.Status.ACTIVE and
                self.start_date <= now <= self.end_date
        )

    @property
    def display_image(self):
        """Return either image URL or uploaded image URL"""
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        return None
