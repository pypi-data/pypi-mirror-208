import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel

from .utils import convert_md_to_html
from .validators import validate_and_vs_ampersand, validate_capitalized


class Entry(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    slug = AutoSlugField(populate_from=["title", "id"])
    title = models.CharField(
        max_length=50,
        help_text="Title of entry.",
        validators=[validate_capitalized, validate_and_vs_ampersand],
    )
    excerpt = models.CharField(
        max_length=50,
        help_text="Short blurb describing entry displayed in list of entries.",
        validators=[validate_capitalized, validate_and_vs_ampersand],
    )
    content = models.TextField(
        help_text="Markdown text formatting, e.g. ##, *, 1., -, etc."
    )
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="entries"
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        return reverse("entries:view_entry", kwargs={"slug": self.slug})

    @property
    def md_content(self) -> str:
        return mark_safe(convert_md_to_html(self.content))

    @classmethod
    def get_for_user(cls, slug: str, user):
        """Simple permission checking"""
        entry = get_object_or_404(cls, slug=slug)
        if entry.author != user:
            raise PermissionDenied()
        return entry
