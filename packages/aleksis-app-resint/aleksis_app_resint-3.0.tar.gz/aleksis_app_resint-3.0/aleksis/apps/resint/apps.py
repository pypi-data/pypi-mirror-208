from django.apps import apps
from django.db import models
from django.db.models import functions
from django.utils.translation import gettext_lazy as _

from aleksis.core.util.apps import AppConfig


class ResintConfig(AppConfig):
    name = "aleksis.apps.resint"
    verbose_name = "AlekSIS – Resint (Public poster)"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2018, 2019, 2020, 2021], "Jonathan Weth", "dev@jonathanweth.de"),
        ([2019], "Julian Leucker", "leuckeju@katharineum.de"),
        ([2020, 2021], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2022], "Dominik George", "dominik.george@teckids.org"),
    )

    @classmethod
    def get_all_scopes(cls) -> dict[str, str]:
        """Return all OAuth scopes and their descriptions for this app."""
        LiveDocument = apps.get_model("resint", "LiveDocument")
        label_prefix = _("Access PDF file for live document")
        scopes = dict(
            LiveDocument.objects.annotate(
                scope=functions.Concat(
                    models.Value(f"{LiveDocument.SCOPE_PREFIX}_"),
                    models.F("slug"),
                    output_field=models.CharField(),
                ),
                label=functions.Concat(models.Value(f"{label_prefix}: "), models.F("name")),
            )
            .values_list("scope", "label")
            .distinct()
        )
        return scopes
