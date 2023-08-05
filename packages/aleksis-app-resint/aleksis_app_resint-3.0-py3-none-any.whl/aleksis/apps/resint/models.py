from datetime import datetime
from typing import Any, Optional

from django.core.files import File
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import reversion
from calendarweek import CalendarWeek
from calendarweek.django import i18n_day_name_choices_lazy
from celery.result import allow_join_result
from celery.states import SUCCESS
from reversion.models import Revision, Version

from aleksis.core.mixins import ExtensibleModel, ExtensiblePolymorphicModel
from aleksis.core.models import DynamicRoute
from aleksis.core.util.pdf import generate_pdf_from_template


class PosterGroupDynamicRoute(DynamicRoute):
    @classmethod
    def get_dynamic_routes(cls):
        poster_groups = PosterGroup.objects.all()

        dynamic_routes = []

        for poster_group in poster_groups:
            dynamic_routes.append(cls.get_route_data(poster_group))

        return dynamic_routes

    @classmethod
    def get_route_data(cls, instance):
        dynamic_route = {}

        dynamic_route["parent_route_name"] = ""

        dynamic_route["route_path"] = reverse("poster_show_current", args=[instance.slug])
        dynamic_route["route_name"] = f"resint.posterGroup.{instance.slug}"

        dynamic_route["display_account_menu"] = False
        dynamic_route["display_sidenav_menu"] = instance.show_in_menu
        dynamic_route["menu_new_tab"] = True

        dynamic_route["menu_title"] = instance.name
        dynamic_route["menu_icon"] = "mdi-file-pdf-box"

        dynamic_route["route_permission"] = "" if instance.public else "resint.view_poster_pdf_menu"

        return dynamic_route


class PosterGroup(ExtensibleModel):
    """Group for time-based documents, called posters."""

    slug = models.SlugField(
        verbose_name=_("Slug used in URL name"),
        help_text=_("If you use 'example', the filename will be 'example.pdf'."),
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    publishing_day = models.PositiveSmallIntegerField(
        verbose_name=_("Publishing weekday"), choices=i18n_day_name_choices_lazy()
    )
    publishing_time = models.TimeField(verbose_name=_("Publishing time"))
    default_pdf = models.FileField(
        upload_to="default_posters/",
        verbose_name=_("Default PDF"),
        help_text=_("This PDF file will be shown if there is no current PDF."),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )

    show_in_menu = models.BooleanField(default=True, verbose_name=_("Show in menu"))
    public = models.BooleanField(default=False, verbose_name=_("Show for not logged-in users"))

    class Meta:
        verbose_name = _("Poster group")
        verbose_name_plural = _("Poster groups")
        constraints = [
            models.UniqueConstraint(fields=["site_id", "name"], name="unique_site_name"),
            models.UniqueConstraint(fields=["site_id", "slug"], name="unique_site_slug"),
        ]
        permissions = [
            ("view_poster_of_group", _("Can view all posters of this group")),
            ("upload_poster_to_group", _("Can upload new posters to this group")),
            ("change_poster_of_group", _("Can change all posters of this group")),
            ("delete_poster_of_group", _("Can delete all posters of this group")),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.publishing_day_name}, {self.publishing_time})"

    @property
    def publishing_day_name(self) -> str:
        """Return the full name of the publishing day (e. g. Monday)."""
        return i18n_day_name_choices_lazy()[self.publishing_day][1]

    @property
    def filename(self) -> str:
        """Return the filename for the currently valid PDF file."""
        return f"{self.slug}.pdf"

    @property
    def current_poster(self) -> Optional["Poster"]:
        """Get the currently valid poster."""
        # Get current date with year and calendar week
        current = timezone.datetime.now()
        cw = CalendarWeek.from_date(current)

        # Create datetime with the friday of the week and the toggle time
        day = cw[self.publishing_day]
        day_and_time = timezone.datetime.combine(day, self.publishing_time)

        # Check whether to show the poster of the next week or the current week
        if current > day_and_time:
            cw += 1

        # Look for matching PDF in DB
        try:
            obj = self.posters.get(year=cw.year, week=cw.week)
            return obj

        # Or show the default PDF
        except Poster.DoesNotExist:
            return None


def _get_current_year() -> int:
    """Get the current year."""
    return timezone.now().year


calendar_weeks = [(cw, str(cw)) for cw in range(1, 53)]


class Poster(ExtensibleModel):
    """A time-based document."""

    group = models.ForeignKey(
        to=PosterGroup,
        related_name="posters",
        on_delete=models.CASCADE,
        verbose_name=_("Poster group"),
    )
    week = models.PositiveSmallIntegerField(
        verbose_name=_("Calendar week"),
        validators=[MinValueValidator(1), MaxValueValidator(53)],
        default=CalendarWeek.current_week,
        choices=calendar_weeks,
    )
    year = models.PositiveSmallIntegerField(verbose_name=_("Year"), default=_get_current_year)
    pdf = models.FileField(
        upload_to="posters/",
        verbose_name=_("PDF"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["site_id", "week", "year", "group"], name="unique_site_week_year"
            )
        ]
        verbose_name = _("Poster")
        verbose_name_plural = _("Posters")

    def __str__(self) -> str:
        return f"{self.group.name}: {self.week}/{self.year}"

    @property
    def valid_from(self) -> datetime:
        """Return the time this poster is valid from."""
        cw = CalendarWeek(week=self.week, year=self.year) - 1
        day = cw[self.group.publishing_day]
        return timezone.datetime.combine(day, self.group.publishing_time)

    @property
    def valid_to(self) -> datetime:
        """Return the time this poster is valid to."""
        cw = CalendarWeek(week=self.week, year=self.year)
        day = cw[self.group.publishing_day]
        return timezone.datetime.combine(day, self.group.publishing_time)


class LiveDocument(ExtensiblePolymorphicModel):
    """Model for periodically/automatically updated files."""

    SCOPE_PREFIX = "live_document_pdf"

    template = None

    slug = models.SlugField(
        verbose_name=_("Slug"),
        help_text=_("This will be used for the name of the current PDF file."),
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))

    current_file = models.FileField(
        upload_to="live_documents/",
        blank=True,
        verbose_name=_("Current file"),
        editable=False,
    )
    last_update_triggered_manually = models.BooleanField(
        default=False, verbose_name=_("Was the last update triggered manually?"), editable=False
    )

    @property
    def last_version(self) -> Optional[Revision]:
        """Get django-reversion version of last file update."""
        versions = Version.objects.get_for_object(self).order_by("revision__date_created")
        if versions.exists():
            return versions.last()
        return None

    @property
    def last_update(self) -> Optional[datetime]:
        """Get datetime of last file update."""
        last_version = self.last_version
        if last_version:
            return last_version.revision.date_created
        return None

    def get_current_file(self) -> Optional[File]:
        """Get current file."""
        if not self.current_file:
            self.update()
        return self.current_file

    @property
    def filename(self) -> str:
        """Get the filename without path of the PDF file."""
        return f"{self.slug}.pdf"

    @property
    def scope(self) -> str:
        """Return OAuth2 scope name to access PDF file via API."""
        return f"{self.SCOPE_PREFIX}_{self.slug}"

    def save(self, *args, **kwargs):
        with reversion.create_revision():
            super().save(*args, **kwargs)

    def get_context_data(self) -> dict[str, Any]:
        """Get context to pass to the PDF template."""
        return {}

    def update(self, triggered_manually: bool = True):
        """Update the file with a new version.

        Has to be implemented by subclasses.
        """
        if not self.template:
            raise NotImplementedError("Subclasses of LiveDocument must implement update()")

        file_object, result = generate_pdf_from_template(self.template, self.get_context_data())
        with allow_join_result():
            result.wait()
            file_object.refresh_from_db()
            if result.status == SUCCESS and file_object.file:
                self.last_update_triggered_manually = triggered_manually
                self.current_file.save(self.filename, file_object.file.file)
                self.save()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Live document")
        verbose_name_plural = _("Live documents")
